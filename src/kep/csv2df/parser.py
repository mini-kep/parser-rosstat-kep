"""Parse [(csv_segment, pdef)... ] inputs into Table() instances using
   parsing specification.

Main call:
   tables = get_tables(rows, SPEC)

"""

from enum import Enum, unique
from collections import OrderedDict as odict

import kep.csv2df.util_row_splitter as splitter
from kep.csv2df.util_label import make_label


__all__ = ['extract_tables']


def extract_tables(csv_segment, pdef):
    """Extract tables from *csv_segment* list Rows instances using
       *pdef* parsing defintion.
    """
    tables = split_to_tables(csv_segment)
    tables = parse_tables(tables, pdef)
    #verify_tables(tables, pdef)
    return [t for t in tables if t.label in pdef.required]


def parse_tables(tables, pdef):
    # assign reader function    
    tables = [t.set_splitter(pdef.reader) for t in tables]    
    # parse tables to obtain labels - set label and splitter
    tables = [t.set_label(pdef.mapper, pdef.units) for t in tables]    
    # assign trailing units
    def fix_multitable_units(tables):
        """For tables without *varname* - copy *varname* from previous table.
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

#    # [4, 5, 12, 13, 17]
#    VALID_ROW_LENGTHS = list(splitter.FUNC_MAPPER.keys())
    KNOWN = "+"
    UNKNOWN = "-"

    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows

        self.lines = odict((row.name, self.UNKNOWN) for row in headers)
        self.coln = max(len(row) for row in self.datarows)
        self.splitter_func = None
       
        self.varname = None
        self.unit = None

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

    def set_splitter(self, reader):
        self.splitter_func = splitter.get_splitter(reader or self.coln)
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
        return "Table(\n    headers={},\n    datarows={})" \
               .format(repr(self.headers), repr(self.datarows))


if __name__ == "__main__": # pragma: no cover
    from kep.csv2df.reader import Row
    rows = [
        Row(['Объем ВВП, млрд.рублей / Gross domestic product, bln rubles']), 
        Row(['1999', '4823', '901', '1102', '1373', '1447']), 
        Row(['2000', '7306', '1527', '1697', '2038', '2044'])
    ]
    t = list(split_to_tables(rows))


#    from kep.config import InterimCSV, LATEST_DATE
#    import kep.csv2df.reader as reader
#    import kep.csv2df.specification as spec
#
#    year, month = LATEST_DATE
#    csv_path = InterimCSV(year, month).path
#    with reader.open_csv(csv_path) as csvfile:
#        parsed_tables = []
#        for csv_segment, pdef in reader.Reader(csvfile, spec.SPEC).items():
#            tables = extract_tables(csv_segment, pdef)
#            parsed_tables.extend(tables)
#
#        for t in tables:
#            print()
#            print(t)
