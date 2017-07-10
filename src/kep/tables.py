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

from . import files
from . import splitter
from .rows import Rows
from .cfg import SPEC
from .cfg import UNITS

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
    """For tables without *header.varname* copy *header.varname*
       from previous table. Applies to tables without unknown rows.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.header.varname is None and not table.header.has_unknown_lines():
            table.header.varname = prev_table.header.varname


def check_required_labels(tables, pdef):
    labels_required = [make_label(varname, unit) for varname, unit in pdef.required]
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in labels_required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels: {}".format(labels_missed))

class Tables:
    """Extract tables from *csv_path*"""

    def __init__(self, csv_path, spec=SPEC, units=UNITS, holder_class=Rows):
        self.spec = spec        
        self.tables = []
        rows = holder_class(csv_path)        
        # use additional parsing definitions first
        for pdef in spec.additional:
            csv_segment = rows.pop(pdef)
            _tables = self.extract_tables(csv_segment, pdef, units)
            self.tables.extend(_tables)
        # use default parsing definition on remaining rows
        pdef = spec.main
        csv_segment = rows.remaining_rows()
        _tables = self.extract_tables(csv_segment, pdef, units)
        self.tables.extend(_tables)

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

    def get_defined(self):
        return [t for t in self.tables if t.is_defined()]

    def get_required(self):
        required_labels = [make_label(*req) for req in self.spec.required()]
        return [t for t in self.get_defined() if t.label in required_labels]
    

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

    def __init__(self, headers, datarows):
        # WONTFIX: naming with three headers in one line
        self.header = Header(headers)
        self.datarows = datarows
        self.coln = max(row.len() for row in self.datarows)
        self.splitter_func = None

    def parse(self, pdef, units):
        varnames_mapper = pdef.headers
        units_mapper = units        
        self.header.pick_varname(varnames_mapper)
        self.header.pick_unit(units_mapper)        
        funcname = pdef.reader
        self.set_splitter(funcname)
        return self

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
        vn = self.header.varname
        u = self.header.unit
        if vn and u:
            return make_label(vn, u)
        else:
            return None

    def is_defined(self):
        return bool(self.label and self.splitter_func)

    def __str__(self):
        return "\n".join(["Table {}".format(self.label),
                          "columns: {}".format(self.coln),
                          str(self.header),
                          "data:",
                          '\n'.join([str(row) for row in self.datarows]),
                          ])

    def __repr__(self):
        return "Table {} ".format(self.label) + \
               "(headers: {}, ".format(len(self.header.textlines)) + \
               "datarows: {})".format(len(self.datarows))


class Header:
    """Table header. Used to extract variable label."""

    KNOWN = "+"
    UNKNOWN = "-"

    def __init__(self, rows):
        self.varname = None
        self.unit = None
        self.rows = [x for x in rows]
        self.lines = odict((row.name, self.UNKNOWN) for row in self.rows)  
        
    def pick_varname(self, varnames_dict):
        for row in self.rows:
            varname = row.get_varname(varnames_dict)
            if varname:            
                self.varname = varname          
                self.lines[row.name] = self.KNOWN
                
    def pick_unit(self, units_dict):
         for row in self.rows:
            unit = row.get_unit(units_dict)
            if unit:
                self.unit = unit
                self.lines[row.name] = self.KNOWN
                
    def has_unknown_lines(self):
        return self.UNKNOWN in self.lines.values()

    def __str__(self):
        show = ["varname: {}, unit: {}".format(self.varname, self.unit)]
        show.append("headers:")
        show.extend(["{} <{}>".format(v, k) for k, v in self.lines.items()])
        return "\n".join(show)


if __name__ == "__main__":
    csv_path = files.locate_csv()
    tables = Tables(csv_path).get_required()
    for t in tables:
        print()
        print(t)