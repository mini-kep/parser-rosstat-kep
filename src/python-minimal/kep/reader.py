import io 
import csv
from enum import Enum, unique
import re
from copy import copy

import kep.filters as filters
import kep.row as row_model
from kep.label import make_label
from kep.units import UnitMapper
from kep.commands import CommandList
from kep.util import iterate

# convert CSV fle to Table() instances

def read_csv(file):
    """Read csv file as list of lists / matrix"""
    with open(file, 'r', encoding='utf-8') as f:
        read_bytes_as_csv(f)
            
def read_bytes_as_csv(f):
    for row in csv.reader(f, delimiter='\t', lineterminator='\n'):
         yield row

def import_tables(file):
    """Wraps read_csv() and split_to_tables() into one call."""
    return list(split_to_tables(read_csv(file)))

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

    #FIXME: may omit in favour of direct_row_format
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

class Container:
    def __init__(self, text: str, base_units: dict):
        tables = import_tables_from_string(text)
        self.incoming_tables = list(tables)
        self.tables = [] 
        self.parsed_tables = []
        self.curname = None
        self.base_mapper = UnitMapper(base_units)
        
    def push(self):
        self.parsed_tables.extend([t for t in self.tables if t])
        
    def init(self):
        self.tables = self.incoming_tables 

    def start_with(self, start_strings):
        self.init()
        start_strings = iterate(start_strings) 
        for i, t in enumerate(self.tables):
            if t.contains_any(start_strings):
                break
        self.tables = self.tables[i:]
        return self    
        
    def end_with(self, end_strings):
        end_strings = iterate(end_strings) 
        we_are_in_segment = True
        for i, t in enumerate(self.tables):
            if t.contains_any(end_strings):
                we_are_in_segment = False
            if not we_are_in_segment:    
                break
        self.tables = self.tables[:i]
        return self
    
    def assign_units(self, unit):
        for t in self.tables:
            t.unit = unit
        return self
   
    def set_name(self, name):
        self.curname = name
        
    def attach_headers(self, headers):
        headers = iterate(headers) 
        for t in self.tables:
           if t.contains_any(headers):
                t.name = self.curname 
        return self        

    def set_units(self, units):
        self.units = iterate(units)

    def parse_units(self):
        for i, t in enumerate(self.tables):
            for header in t.headers:
                unit = self.base_mapper.extract(header)
                if unit:
                    t.unit = unit

    def prev_next_pairs(self):
        return zip([None] + self.tables[:-1], self.tables) 

    # TODO
    def trail_down_units(self):
        """Assign trailing variable names in tables.
           Trailing names are defined in leading table and pushed down
           to following tables, if their unit is specified in namers.units
        """
#        for prev_table, table in self.prev_next_pairs():
#            if (table.unit is None
#                and prev_table.unit is not None
#                and table.name):
#                table.unit = prev_table.unit
        pass        


    # TODO
    def trail_down_names(self):
        """Assign trailing variable names in tables.
           Trailing names are defined in leading table and pushed down
           to following tables, if their unit is specified in namers.units
        """
        _units = copy(self.units)
        for i, table in enumerate(self.tables):
            if not _units:
                break
            if table.name and table.unit in _units:
                _units.remove(table.unit)
            if i >= 1 and table.name is None and table.unit in _units:
                table.name = self.tables[i-1].name
                _units.remove(table.unit)

    # TODO
    def parse_units_with(self, mapper: dict={}):
        for t in self.tables:
            pass
        return self
    
    def require(self, string):
        label, freq, date, value = string.split(' ')
        value = float(value)
        dp = row_model.Datapoint(label, freq, date, value) 
        assert dp in self.datapoints
    
    @property
    def datapoints(self):
        return list(self.emit_datapoints())
    
    def emit_datapoints(self):
        for t in self.parsed_tables:
            if t:
                for x in t.emit_datapoints():
                    yield x

    @property
    def labels(self):
        return [t.label for t in self.parsed_tables] 

    def apply(self, commands_source):
        for func in CommandList(commands_source).functions():
            func(self)


#TODO:
#    
#    
#    def put_trailing_names(self, parser):
#
#
#    def put_trailing_units(self, parser):

# Fails on empty row 
#    if filters.is_year(row[0]):
# IndexError: list index out of range

