"""Parse raw CSV file into Tables() instances using parsing specification from spec.py

Main call:
   tables = Tables(rowstack).get_required():

"""

from enum import Enum, unique
from collections import OrderedDict as odict
import itertools
import warnings

from kep import splitter
from kep.rows import RowStack
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


def missed_labels(tables, pdef):
    labels_required = [make_label(varname, unit)
                       for varname, unit in pdef.get_required_labels()]
    labels_in_tables = [t.label for t in tables]
    return [x for x in labels_required if x not in labels_in_tables]


class Tables:
    """Extract tables from *csv_path* using *Rows(csv_path)*.

       Parsing procedure:
       - cut out a segment of csv file as delimited by start and end line makers
       - hold remaining parts of csv file for further parsing
       - break csv segment into tables, each table containing headers and data rows
       - parse table headers to obtain variable name ("GDP") and unit ("bln_rub")"""

    def __init__(self, _rows, spec=SPEC, units=UNITS):
        self.rowstack = RowStack(_rows)
        self.spec = spec
        self.units = units
        self.required = [make_label(varname, unit)
                         for varname, unit in spec.get_required_labels()]
        self.make_queue()

    def make_queue(self):
        """Init list of csv segments and parsing definitons"""
        self.to_parse = []
        for pdef in self.spec.get_segment_parsing_definitions():
            # find segemnt limits
            start, end = pdef.scope.get_bounds(self.rowstack.rows)
            # pop csv segment
            csv_segment = self.rowstack.pop(start, end)
            # get current parsing definition
            self.to_parse.append([csv_segment, pdef])
        csv_segment = self.rowstack.remaining_rows()
        pdef = self.spec.get_main_parsing_definition()
        self.to_parse.append([csv_segment, pdef])

    def yield_tables(self):
        for csv_segment, pdef in self.to_parse:
            for t in self.extract_tables(csv_segment, pdef, self.units):
                yield t

    @staticmethod
    def extract_tables(csv_segment, pdef, units_dict):
        # yield tables from csv_segment
        tables = split_to_tables(csv_segment)
        # parse tables to obtain labels
        varnames_dict = pdef.get_varname_mapper()
        tables = [t.set_label(varnames_dict, units_dict) for t in tables]
        tables = [t.set_splitter(pdef.reader) for t in tables]
        # another run to assign trailing units to some tables
        fix_multitable_units(tables)
        # were all required tables read?
        labels_missed = missed_labels(tables, pdef)
        if labels_missed:
            raise ValueError("Missed labels: {}".format(labels_missed))
        return tables

    def get(self):
        return list(self.yield_tables())

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
    VALID_ROW_LENGTHS = list(splitter.FUNC_MAPPER.keys())
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
        return self

    def set_splitter(self, funcname):
        self.splitter_func = splitter.get_splitter(funcname or self.coln)
        return self

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
    from kep import files
    from kep import rows
    csv_path = files.locate_csv()
    _rows = rows.read_csv(csv_path)
    tables = Tables(_rows).get_required()
    for t in tables:
        print()
        print(t)
