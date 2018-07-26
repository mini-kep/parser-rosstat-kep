import io
import csv
from enum import Enum, unique
import re

import kep.filters as filters
import kep.row as row_model
from kep.util import make_label


# WONTFIX:
# Fails on empty row
#    if filters.is_year(row[0]):
# IndexError: list index out of range



# convert CSV fle to Table() instances


def read_csv(file):
    """Read csv file as list of lists / matrix"""
    with open(file, 'r', encoding='utf-8') as f:
        read_bytes_as_csv(f)


def read_bytes_as_csv(f):
    for row in csv.reader(f, delimiter='\t', lineterminator='\n'):
        yield row


def import_tables_from_string(text):
    """Wraps read_csv() and split_to_tables() into one call."""
    matrix = read_bytes_as_csv(io.StringIO(text))
    return list(split_to_tables(matrix))


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
    def __init__(self, headers,
                 datarows,
                 row_format=None,
                 name=None,
                 unit=None):
        self._headers = headers
        self.headers = [x[0] for x in headers if x[0]]
        self.datarows = datarows
        self.name = name
        self.unit = unit
        if row_format:
            self.row_format = row_format
        else:
            self.row_format = row_model.get_format(row_length=self.coln)

    def __eq__(self, x):
        return repr(self) == repr(x)

    def __bool__(self):
        return (self.name is not None) and (self.unit is not None)

    @property
    def label(self):
        if self:
            return make_label(self.name, self.unit)
        return None

    @property
    def coln(self):
        return max([len(row) for row in self.datarows])

    def contains_any(self, strings):
        for header in self.headers:
            for s in strings:
                if re.search(r'\b{}'.format(s), header):
                    return s
        return None

    # FIXME: may omit in favour of direct_row_format
    def assign_row_format(self, key):
        self.row_format = row_model.assign_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in row_model.emit_datapoints(row, _label, self.row_format):
                yield d

    def __repr__(self):
        items = [f'Table(name={repr(self.name)}',
                 f'unit={repr(self.unit)}',
                 f'row_format={repr(self.row_format)}',
                 f'headers={self.headers}',
                 f'datarows={self.datarows[0]}'
                 ]
        return ',\n      '.join(items)