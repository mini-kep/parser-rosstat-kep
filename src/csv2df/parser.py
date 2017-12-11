"""Parse [(csv_segment, pdef)... ] inputs into Table() instances using
   parsing specification.

Main call:
   tables = get_tables(rows, SPEC)

"""

from enum import Enum, unique
from collections import OrderedDict as odict

import csv2df.util_row_splitter as splitter
from csv2df.util_label import make_label


__all__ = ['extract_tables']


def extract_tables(csv_segment, pdef):
    """Extract tables from *csv_segment* list Rows instances using
       *pdef* parsing defintion.
    """
    tables = split_to_tables(csv_segment)
    tables = parse_tables(tables, pdef)
    verify_tables(tables, pdef)
    return [t for t in tables if t.label in pdef.required]


def parse_tables(tables, pdef):
    # parse tables to obtain labels - set label and splitter
    tables = [t.set_label(pdef.varnames_dict, pdef.units_dict) for t in tables]
    tables = [t.set_splitter(pdef.funcname) for t in tables]
    # assign trailing units
    def fix_multitable_units(tables):
        """For tables without *varname*-  copy *varname* from previous table.
           Applies to tables where all rows are known rows.
        """
        for prev_table, table in zip(tables, tables[1:]):
            if table.varname is None and not table.has_unknown_lines():
                table.varname = prev_table.varname
    fix_multitable_units(tables)
    return tables


def verify_tables(tables, pdef):
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in pdef.required if x not in labels_in_tables]
    if labels_missed:
        import pdb
        pdb.set_trace()
        raise ValueError("Missed labels: {}".format(labels_missed))

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
        self.coln = max(len(row) for row in self.datarows)
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
        return "Table(headers={},\ndatarows={})".format(repr(self.headers),
                                                        repr(self.datarows))
def get_tables(year, month):
    from config import InterimCSV
    import csv2df.specification as spec
    import csv2df.reader as reader
        
    parsed_tables = []
    csv_path = InterimCSV(year, month).path    
    with reader.open_csv(csv_path) as csvfile:
        for csv_segment, pdef in reader.Reader(csvfile, spec.SPEC).items():
            tables = extract_tables(csv_segment, pdef)
            parsed_tables.extend(tables)
    return parsed_tables      
    
    

if __name__ == "__main__":
    from config import InterimCSV, LATEST_DATE
    import csv2df.reader as reader
    import csv2df.specification as spec

    year, month = LATEST_DATE
    csv_path = InterimCSV(year, month).path
    with reader.open_csv(csv_path) as csvfile:
        parsed_tables = []
        for csv_segment, pdef in reader.Reader(csvfile, spec.SPEC).items():
            tables = extract_tables(csv_segment, pdef)
            parsed_tables.extend(tables)

        for t in tables:
            print()
            print(t)
            
    tables = get_tables(year, month)        
