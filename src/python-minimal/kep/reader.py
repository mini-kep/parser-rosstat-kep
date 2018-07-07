from collections import namedtuple
"""Parse data from CSV files

Calls:

    import reader
    import saver

    values = reader.to_values(path, unit_mapper_dict, namers)
    dfa, dfs, dfq = saver.unpack_dataframes()

Inputs:
  - csv file
  - text to unit mapping dictionary {'млрд.руб.': 'bln_rub'}
  - variable name, text headers and units:
      {'name': 'INDPRO',
       'headers': ['Индекс промышленного производства'],
       'units': ['yoy', 'rog', 'ytd']}

Pseudocode
==========

 reader.py:
 1. read CSV
 2. extract individual tables form CSV
 3. for each table:
   - identify unit of measurement
   - identify variable name
   - get values based on columns format like "YQQQQMMMMMMMMMMMM"
 saver.py:
 4. combine data from tables into three dataframes based on frequency
   - dfa (annual data)
   - dfq (quarterly data)
   - dfm (monthly data)
 5. adjust dataframes

"""

import csv
from enum import Enum, unique


import kep.filters as filters
import kep.row as row_model
from kep.label import make_label


# convert CSV to Table() instances


def import_tables(file):
    """Wraps read_csv() and split_to_tables() into one call."""
    return list(split_to_tables(read_csv(file)))


def read_csv(file):
    """Read csv file as list of lists / matrix"""
    fmt = dict(delimiter='\t', lineterminator='\n')
    with open(file, 'r', encoding='utf-8') as f:
        for row in csv.reader(f, **fmt):
            yield row


@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2


def split_to_tables(csv_rows):
    """Yield Table() instances from *csv_rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in csv_rows:
        # is data row?
        if filters.is_year(row[0]):
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:
                # table ended, emit it
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.HEADERS
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class Table:
    def __init__(self, headers, datarows, name=None, unit=None):
        self._headers = headers
        self.headers = [x[0] for x in headers if x[0]]
        self.datarows = datarows
        self.name = name
        self.unit = unit
        self.row_format = row_model.get_format(row_length=self.coln)

    def __eq__(self, x):
        return str(self) == str(x)

    @property
    def label(self):
        return make_label(self.name, self.unit)

    @property
    def coln(self):
        return max([len(row) for row in self.datarows])

    def is_defined(self):
        return self.name and self.unit

    def contains_any(self, strings):
        return any([self.headers_contain(s) for s in strings])

    def headers_contain(self, string):
        for x in self.headers:
            if string in x:
                return True
        return False

    def assign_row_format(self, key):
        self.row_format = row_model.assign_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in row_model.emit_datapoints(row, _label, self.row_format):
                yield d

    def __repr__(self):
        return ',\n      '.join([f"Table(name={repr(self.name)}",
                                 f"unit={repr(self.unit)}",
                                 f"row_format={repr(self.row_format)}",
                                 f'headers={self.headers}',
                                 f'datarows={self.datarows}'])

# table parsing


def put_units(tables, unit_mapper_dict):
    for table in tables:
        for text, unit in unit_mapper_dict.items():
            if table.headers_contain(text):
                table.unit = unit
                break


def put_names(tables, namers):
    for namer in namers:
        we_are_in_segment = False
        for t in tables:
            if t.contains_any(namer.starts):
                we_are_in_segment = True
            if (t.contains_any(namer.headers)
                and t.name is None
                    and we_are_in_segment):
                t.name = namer.name
                break
            if namer.ends and t.contains_any(namer.ends):
                break


def put_trailing_names_and_readers(tables, namers):
    """Assign trailing variable names in tables.
       Trailing names are defined in leading table and pushed down
       to following tables, if their unit is specified in namers.units
    """
    for namer in namers:
        _units = namer.units.copy()
        for prev_table, table in zip(tables[:-1], tables[1:]):
            if (table.name is None
                and prev_table.name is not None
                    and table.unit in _units):
                table.name = prev_table.name
                table.row_format = prev_table.row_format
                _units.remove(table.unit)


def put_readers(tables, namers):
    namers = [n for n in namers if n.reader]
    for namer in namers:
        for table in tables:
            if table.name == namer.name:
                table.assign_row_format(namer.reader)


def parsed_tables(filename, unit_mapper_dict, namers):
    tables = import_tables(filename)
    put_units(tables, unit_mapper_dict)
    put_names(tables, namers)
    put_readers(tables, namers)
    put_trailing_names_and_readers(tables, namers)
    return tables


def emit_datapoints(tables):
    for t in tables:
        if t.name and t.unit:
            for x in t.emit_datapoints():
                 yield x    

def to_values(filename, unit_mapper_dict, namers):
    tables = parsed_tables(filename, unit_mapper_dict, namers)
    return [x for x in emit_datapoints(tables)]

