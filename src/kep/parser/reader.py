"""Convert CSV file to Table() instances. Use get_tables(filepath)."""

from enum import Enum, unique
import re
import pprint

from kep.parser.row import get_row_format, emit_datapoints
from kep.util import make_label


__all__ = ['get_tables', 'split_csv', 'Table']

# 'I' accounts for quarterly headers in I, II, III and IV
RE_LITERALS = re.compile(r'[а-яI]')

def has_literals(s: str) -> bool:
    return re.search(RE_LITERALS, s)

def is_data_row(row: str) -> bool:
    return not has_literals(row)

# data import
            
def is_allowed(row):
    return row and '_' not in row

def get_tables(filepath: str):    
    rows = filter(is_allowed, read_csv(filepath))
    table_dicts = split_csv(rows)
    return [Table(**td) for td in table_dicts]

def read_csv(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        for row in f.read().splitlines():
            yield row  

# split to tables

@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2


def as_dict(headers, datarows):
    return dict(header_strings=headers, datarow_strings=datarows)


def split_csv(rows):
    """Split *csv_rows* by_table. Each table is a tuple of header and data rows.
       
       Args:
           csv_rows - list of rows or iterator
           is_data_row - function
           
       Returns:
           list of dictionaries
    """
    result = []
    datarows, headers = [], []
    state = State.INIT
    for row in rows:
        # is this a data row?
        if is_data_row(row):
            # this is a data row!            
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:
                # table ended, emit it
                t = as_dict(headers, datarows)
                result.append(t)
                # reset containers
                headers = []
                datarows = []
            headers.append(row)
            state = State.HEADERS
    # still have some data left, emit it too
    if len(headers) > 0 and len(datarows) > 0:
        t = as_dict(headers, datarows)
        result.append(t)
    return result

        
class Table:
    """Representation of a table from CSV file."""
    def __init__(self, header_strings,
                 datarow_strings,
                 row_format=None,
                 name=None,
                 unit=None):
        self.headers = header_strings
        self._datarow_strings = datarow_strings
        self.name = name
        self.unit = unit
        self.row_format = row_format
        
    def __eq__(self, x):
        return self.__dict__ == x.__dict__

    def __bool__(self):
        return (self.name is not None) and (self.unit is not None)

    @property    
    def datarows(self):
        return [[x for x in row.split('\t')] for row in self._datarow_strings]    

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
        rows = self.datarows
        label = self.label
        if self.row_format is None:
             self.row_format = get_row_format(rows)        
        for row in self.datarows:
            for d in emit_datapoints(row, label, self.row_format):
                yield d

    def __repr__(self):
        items = ['Table(name=%r' % self.name,
                 'unit=%r'% self.unit,
                 'row_format=%r' % self.row_format,
                 'header_strings=%s' % pprint.pformat(self.headers),
                 'datarow_strings=%s)' % pprint.pformat(self._datarow_strings)   
                 ]
        return ',\n      '.join(items)