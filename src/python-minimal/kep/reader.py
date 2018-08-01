import io
import csv
from enum import Enum, unique
import re
import pprint

import kep.filters as filters
import kep.row as row_model
from kep.util import make_label
from kep.interface import accept_filename_or_string

# WONTFIX:
# Fails on empty row
#    if filters.is_year(row[0]):
# IndexError: list index out of range



# convert CSV fle to Table() instances


def read_csv(filename):
    """Read csv file as list of lists / matrix"""
    with open(filename, 'r', encoding='utf-8') as f:
        return read_bytes_as_csv(f)

def read_csv_from_string(text:str):
    """Read csv file as list of lists / matrix"""
    return read_bytes_as_csv(io.StringIO(text))

def read_bytes_as_csv(f):
    for row in csv.reader(f, delimiter='\t', lineterminator='\n'):
        yield row

@accept_filename_or_string
def import_tables_from_string(text):
    """Wraps read_csv() and split_to_tables() into one call."""
    gen = read_csv_from_string(text)
    return list(split_to_tables(gen))


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

ROW_FORMAT_DICT = {len(x): x for x in [
    'YAQQQQMMMMMMMMMMMM',
    'YAQQQQ',
    'YAMMMMMMMMMMMM',
    'YMMMMMMMMMMMM',
    'YQQQQ',
    'XXXX',
    'XXX',
    'X'*11]}
    
def get_row_format(coln: int):
    return ROW_FORMAT_DICT[coln]    

class Table:
    def __init__(self, header_rows,
                 data_rows,
                 row_format=None,
                 name=None,
                 unit=None):
        self.header_rows = header_rows
        self.datarows = data_rows
        self.name = name
        self.unit = unit
        self.row_format = self.get_row_format()
        # overrride if supplied
        if row_format:
            self.row_format = row_format

    @property
    def headers(self):
        return [x[0] for x in self.header_rows if x[0]]


    def get_row_format(self):
        try:
            return get_row_format(self.coln)
        except KeyError:
            raise ValueError('Cannot define row format', 
                              self.coln,
                              self.datarows)

    def __eq__(self, x):
        return (self.header_rows == x.header_rows 
                and self.datarows == x.datarows
                and self.name == x.name
                and self.unit == x.unit
                and self.row_format == x.row_format)

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

    def emit_datapoints(self):
        _label = self.label # speedup: create label once 
        for row in self.datarows:
            for d in row_model.emit_datapoints(row, _label, self.row_format):
                yield d

    def __repr__(self):
        items = [f'Table(name={repr(self.name)}',
                 f'unit={repr(self.unit)}',
                 f'row_format={repr(self.row_format)}',
                 f'header_rows={pprint.pformat(self.header_rows)}',
                 f'data_rows={pprint.pformat(self.datarows)})'    
                 ]
        return ',\n      '.join(items)