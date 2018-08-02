import io
import csv
from enum import Enum, unique
import re
import pprint

import kep.filters as filters
from kep.row import get_row_format, emit_datapoints
from kep.util import make_label, accept_filename_or_content_string

# WONTFIX:
# Fails on empty row
#    if filters.is_year(row[0]):
# IndexError: list index out of range


__all__ = ['import_tables', 'Table', 'read_csv', 'split_to_tables']

def import_tables(source):
    """Wrap read_csv() and split_to_tables() into one call."""
    gen = read_csv(source)
    return list(split_to_tables(gen))

# CSV import

def read_csv_from_file(filename):
    """Read csv file as list of lists / matrix"""     
    with open(filename, encoding='utf-8', newline='') as f:
        for row in csv.reader(f, delimiter='\t', lineterminator='\n'):
             yield row


def read_bytes_as_csv(f):
    for row in csv.reader(f, delimiter='\t', lineterminator='\n'):
        yield row


@accept_filename_or_content_string
def read_csv(source):
    return read_bytes_as_csv(io.StringIO(source))

# convert list of csv rows to Table() instances

@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2


def split_to_tables(csv_rows):
    """Yield Table() instances from *csv_rows*."""
    csv_rows = filter(filters.is_allowed, csv_rows)
    result = []
    datarows, headers = [], []
    state = State.INIT
    for row in csv_rows:
        # is data row?
        year = filters.clean_year(row[0])
        if year:
            row[0] = year
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:
                # table ended, emit it
                t = headers, datarows
                result.append(t)
                headers = []
                datarows = []
            headers.append(row)
            state = State.HEADERS
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        t = headers, datarows
        result.append(t)
    return result
        
class Table:
    """Representation of a table from CSV file."""
    def __init__(self, headrows,
                 datarows,
                 row_format=None,
                 name=None,
                 unit=None):
        self.headrows = headrows
        self.datarows = datarows
        self.name = name
        self.unit = unit
        self.row_format = row_format or None
        
    @property
    def headers(self):
        """First elements of headrows."""
        return [x[0] for x in self.headrows if x and x[0]]

    def _properties(self):
        return (self.headrows, 
                self.datarows, 
                self.name, 
                self.unit, 
                self.row_format)               

    def __eq__(self, x):
        return self._properties() == x._properties()

    def __bool__(self):
        return (self.name is not None) and (self.unit is not None)

    @property
    def label(self):
        """Variable identifier like 'CPI_rog'"""
        return make_label(self.name, self.unit)

    def contains_any(self, strings):
        """Return largest string found in table headers."""
        for header in self.headers:
            for s in strings:
                if re.search(r'\b{}'.format(s), header):
                    return s
        return ''

    def emit_datapoints(self):
        """Yield Datapoint() instances from table."""
        if self.row_format is None:
             self.row_format = get_row_format(self.datarows)        
        label = self.label # speedup: create label once 
        for row in self.datarows:
            for d in emit_datapoints(row, label, self.row_format):
                yield d

    def __repr__(self):
        items = ['Table(name=%r' % self.name,
                 'unit=%r'% self.unit,
                 'row_format=%r' % self.row_format,
                 'headrows=%s' % pprint.pformat(self.headrows),
                 'datarows=%s)' % pprint.pformat(self.datarows)   
                 ]
        return ',\n      '.join(items)