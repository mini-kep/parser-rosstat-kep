"""Parse raw CSV file into Tables() instances using parsing specification from cfg.py

Main call:
   csv_path = locate_csv(year, month)
   tables = Tables(csv_path).get_required():

Parsing procedure:
   - cut out a segment of csv file as delimited by start and end line makers
   - hold remaining parts of csv file for further parsing
   - break csv segment into tables, each table containing headers and data rows
   - parse table headers to obtain variable name ("GDP") and unit ("bln_rub")

"""

from enum import Enum, unique
from collections import OrderedDict as odict
import itertools
import warnings

from kep import files
from kep import splitter
from kep.rows import CSV
from kep.spec import SPEC
from kep.spec import UNITS

# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)

# label handling
def make_label(vn, unit, sep="_"):
    return vn + sep + unit


def split_label(label):
    return extract_varname(label), extract_unit(label)


def extract_varname(label):
    words = label.split('_')
    return '_'.join(itertools.takewhile(lambda word: word.isupper(), words))


def extract_unit(label):
    words = label.split('_')
    return '_'.join(itertools.dropwhile(lambda word: word.isupper(), words))

# handling tables
def fix_multitable_units(tables):
    """For tables without *varname* copy *varname* from previous table. 
        Applies to tables without unknown rows.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.varname is None and not table.has_unknown_lines():
            table.varname = prev_table.varname


def check_required_labels(tables, pdef):
    """Raise exception if *tables* do not contain any of labels from *pdef.required*."""
    labels_required = [make_label(varname, unit) for varname, unit in pdef.required]
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in labels_required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels: {}".format(labels_missed))

from itertools import chain 

class Tables:
    """Extract tables from *csv_path* using *Rows(csv_path)*."""

    def __init__(self, rowstack, spec=SPEC, units=UNITS):
        self.rowstack = rowstack
        self.spec = spec 
        self.units = units
        self.required = [make_label(varname, unit) for varname, unit in spec.required()]
       
    def yield_tables_from_segments(self):
        # use parsing definitions for segments first
        for scope in self.spec.scopes:
            start, end = scope.get_bounds(self.rowstack.rows)
            csv_segment = self.rowstack.pop(start, end)            
            pdef = scope.definition
            for t in self.extract_tables(csv_segment, pdef, units=self.units):
                yield t
                
    def yield_tables_from_main(self):
        # use default parsing definition on remaining rows
        csv_segment = self.rowstack.remaining_rows()
        pdef = self.spec.main
        for t in self.extract_tables(csv_segment, pdef, units=self.units):
            yield t
            
    def yield_tables(self):        
        return chain(self.yield_tables_from_segments(),             
                     self.yield_tables_from_main())   

    @staticmethod 
    def extract_tables(csv_segment, pdef, units):
        # yield tables from csv_segment
        tables = split_to_tables(csv_segment)
        # parse tables to obtain labels 
        tables = [t.parse(pdef, units) for t in tables]
        # another run to assign trailing units to some tables
        fix_multitable_units(tables)
        # were all required tables read?
        check_required_labels(tables, pdef)
        return tables

    def get(self):
        gen = self.yield_tables()
        return list(gen)
    
    def get_required(self):
        return [t for t in self.get() if t.label in self.required]
    

# classes for split_to_tables()
@unique
class RowType(Enum):
    UNKNOWN = 0
    DATA = 1
    SECTION = 2
    HEADER = 3


@unique
class State(Enum):
    INIT = 1
    DATA = 2
    UNKNOWN = 3


def split_to_tables(rows):
    """Yields Table() instances from *rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        if row.is_datarow():
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:  # table ended
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.UNKNOWN
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class Table:
    """Representation of CSV table, has headers and datarows."""

    # [4, 5, 12, 13, 17]
    VALID_ROW_LENGTHS = list(splitter.ROW_LENGTH_TO_FUNC_MAPPER.keys())
    KNOWN = "+"
    UNKNOWN = "-"
   
    def __init__(self, headers, datarows):
        self.varname = None
        self.unit = None
        self.headers = headers
        self.lines = odict((row.name, self.UNKNOWN) for row in headers)  
        self.datarows = datarows
        self.coln = max(row.len() for row in self.datarows)
        self.splitter_func = None

    def parse(self, pdef, units):
        varnames_dict = pdef.headers
        units_dict = units
        funcname = pdef.reader
        self.set_label(varnames_dict, units_dict)        
        self.set_splitter(funcname)
        return self
    
    def set_label(self, varnames_dict, units_dict):
        for row in self.headers:
            varname = row.get_varname(varnames_dict)
            if varname:            
                self.varname = varname          
                self.lines[row.name] = self.KNOWN
            unit = row.get_unit(units_dict)
            if unit:
                self.unit = unit
                self.lines[row.name] = self.KNOWN

    def set_splitter(self, funcname):
        if funcname:
            # custom reader from pdef has highest priority
            self.splitter_func = splitter.get_custom_splitter(funcname)
        elif self.coln in self.VALID_ROW_LENGTHS:
            # use standard splitters for standard number of columns
            self.splitter_func = splitter.get_splitter(self.coln)
        else:
            # Trying to parse a table without <year> <values> structure.
            # Such tables are currently out of scope of parsing.
            msg = "unexpected row length {}\n{}".format(self.coln, self)
            warnings.warn(msg)

    @property
    def label(self):
        vn = self.varname
        u = self.unit
        if vn and u:
            return make_label(vn, u)
        else:
            return None

    def is_defined(self):
        return bool(self.label and self.splitter_func)

    def has_unknown_lines(self):
        return self.UNKNOWN in self.lines.values()

    def __eq__(self, x):
        return self.headers == x.headers and self.datarows == x.datarows

    def __str__(self):
        show = ["Table {} ({} columns)".format(self.label, self.coln),
                '\n'.join(["{} <{}>".format(v, k) for k, v in self.lines.items()]),
                '\n'.join([str(row) for row in self.datarows])
                 ]
        return "\n".join(show)

    def __repr__(self):
        return "Table(headers={}, datarows={})".format(repr(self.headers),
                                                      repr(self.datarows))


if __name__ == "__main__":    
    csv_path = files.locate_csv()
    rowstack = CSV(csv_path).rowstack 
    tables = Tables(rowstack).get_required()
    for t in tables:
        print()
        print(t)