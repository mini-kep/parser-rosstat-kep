"""Parse CSV file rows into Tables() using parsing specification from spec.py

Main call:
   tables = get_tables(rows, SPEC)

"""

from enum import Enum, unique
from collections import OrderedDict as odict
import warnings

from kep import splitter
from kep.rows import RowStack
from kep.spec import SPEC
from kep.label import make_label

# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)


def fix_multitable_units(tables):
    """For tables without *varname* copy *varname* from previous table.
        Applies to tables without unknown rows.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.varname is None and not table.has_unknown_lines():
            table.varname = prev_table.varname


def extract_tables(csv_segment, pdef):
    """Extract tables from *csv_segment* using *pdef* defintion.
    """
    # yield tables from csv_segment
    tables = split_to_tables(csv_segment)
    # parse tables to obtain labels
    tables = [t.set_label(pdef.varnames_dict, pdef.units_dict) for t in tables]
    tables = [t.set_splitter(pdef.funcname) for t in tables]
    # another run to assign trailing units to some tables
    fix_multitable_units(tables)
    # were all required tables read?
    _labels_in_tables = [t.label for t in tables]
    _labels_missed = [x for x in pdef.required if x not in _labels_in_tables]
    if _labels_missed:
        raise ValueError("Missed labels: {}".format(_labels_missed))
    return [t for t in tables if t.label in pdef.required]


def yield_tables(_rows, spec):
    rowstack = RowStack(_rows)
    for csv_segment, pdef in rowstack.yield_segment_with_defintion(spec):
        for t in extract_tables(csv_segment, pdef):
            yield t


def get_tables(_rows, spec):
    return list(yield_tables(_rows, spec))


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
    tables = get_tables(_rows, SPEC)
    for t in tables:
        print()
        print(t)
