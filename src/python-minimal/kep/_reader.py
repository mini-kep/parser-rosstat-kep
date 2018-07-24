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
import re
from collections import namedtuple

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
        return repr(self) == repr(x)

    @property
    def label(self):
        return make_label(self.name, self.unit)

    @property
    def coln(self):
        return max([len(row) for row in self.datarows])

    def is_defined(self):
        return self.name and self.unit

    def contains_any(self, strings):
        for header in self.headers:
            for s in strings:
                if re.search(r'\b{}'.format(s), header):
                    return s
        return None

    def assign_row_format(self, key):
        self.row_format = row_model.assign_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in row_model.emit_datapoints(row, _label, self.row_format):
                yield d

    def assign_name(self, parser):
        if self.contains_any(parser.headers):
            self.name = parser.name
    
    
    def assign_unit(self, parser):
        for header in self.headers:
            unit = parser.mapper.extract(header)
            if unit:
                self.unit = unit


    def __repr__(self):
        return ',\n      '.join([f"Table(name={repr(self.name)}",
                                 f"unit={repr(self.unit)}",
                                 f"row_format={repr(self.row_format)}",
                                 f'headers={self.headers}',
                                 f'datarows={self.datarows[0]}'
                                 ]
    )

from copy import copy
 
class TableList:
    def __init__(self, tables=[]):
        self.tables = list(tables)
        
    def __getitem__(self, i):
        return self.tables[i]
    
    def __repr__(self):
        return repr(self.tables)
    
    def extend(self, x):
        self.tables.extend(copy(x)) 
        return self        
    
    def remove(self, x):
        for i, t in enumerate(self.tables):
            if t == x:
                del self.tables[i]
        return self        
    
    def defined(self):
        return [t for t in self.tables if t.is_defined()]
            
    def find(self, name=None, unit=None):
        _tables = self.defined()
        if name:
             _tables = filter(lambda t: t.name == name, _tables)
        if unit:
             _tables = filter(lambda t: t.unit == unit, _tables)
        return list(_tables)
    
    @property
    def labels(self):
        return [t.label for t in self.tables if t.is_defined()] 
 
    def segment(self, start_strings, end_strings):
        segment = []  
        we_are_in_segment = False
        for t in self.tables:
            if t.contains_any(start_strings):
                we_are_in_segment = True
            if t.contains_any(end_strings):
                break
            if we_are_in_segment:
                # warning: otherwise table gets modified unexpectedly 
                z = copy(t)
                segment.append(z)
        return TableList(segment)        
    

    def prev_next_pairs(self):
        return zip(self.tables[:-1], self.tables[1:]) 
    
    
    def put_trailing_names(self, parser):
        """Assign trailing variable names in tables.
           Trailing names are defined in leading table and pushed down
           to following tables, if their unit is specified in namers.units
        """
        _units = copy(parser.units)
        for prev_table, table in self.prev_next_pairs():
            if not _units:
                break
            if prev_table.name == parser.name:
               try:
                    _units.remove(prev_table.unit)
               except ValueError:
                    pass                    
            if (table.name is None
                and prev_table.name is not None
                and table.unit in _units):
                table.name = prev_table.name
                print(table.headers)
                print(_units)
                _units.remove(table.unit)


    def put_trailing_units(self, parser):
        """Assign trailing variable names in tables.
           Trailing names are defined in leading table and pushed down
           to following tables, if their unit is specified in namers.units
        """
        for prev_table, table in self.prev_next_pairs():
            if (table.unit is None
                and prev_table.unit is not None
                and table.name):
                table.unit = prev_table.unit


    def apply(self, parser):
        for table in self.tables:
             table.assign_name(parser)
             table.assign_unit(parser)
        self.put_trailing_names(parser)
        self.put_trailing_units(parser)
    
    def emit_datapoints(self):
        for t in self.tables:
            for x in t.emit_datapoints():
                yield x

    def print(self):
        for i, t in enumerate(self.tables):
           print(i, t.headers)

def cut_segment(tables, namer):
    return tables.segment(namer.scope.starts, namer.scope.ends)

# to tests:
assert TableList([1,2,3]).remove(2).tables == [1, 3]    

             
# прочитать все определения
# выбрать определения с границами
#      получить таблицы
#      использовать юнитс или кастом юнитс 
#      добавить имена
# вернуть новый cписок таблиц 
# полуить значения
if __name__ == '__main__':
    from kep.definition.namers import NAMERS
    from paths import PATH_CSV
    filename=PATH_CSV
    namers=NAMERS
    tables = TableList(import_tables(filename))
    res = TableList()
    border_namers = [n for n in namers if n.scope.is_defined()]
    #default_namers = [n for n in namers if not n.scope]
    #for namer in border_namers:
    #    subtables = tables.segment(namer.scope.starts, namer.scope.ends)
    #    subtables.apply(namer)
    #    print(namer, "expects", namer.labels)
    #    print("Found", subtables.labels)
        #if namer.labels != subtables.labels:
        #   print((namer.labels, subtabnamersles.labels))
    #    res.extend(subtables)        
    for i, namer in enumerate(border_namers):
        subtables = cut_segment(tables, namer)
        subtables.apply(namer)
        print(i)        
        print('Expected', namer.labels)
        print('Found', subtables.labels)
        try:
            assert subtables.labels == namer.labels 
        except AssertionError:
            raise AssertionError
        del subtables 
    

    
# to test    
#    from kep.reader import Table
#    p = Parser(name='DINPRO',
#               headers=['Промышленное производство'],
#               custom_mapper_dict={'динозавров в год': 'dins'} 
#               )
#    t = Table(headers=[['Промышленное производство, динозавров в год']], 
#              datarows=[[2018, 40, 10, 10, 10]])
#    
#    assign_name(t, p)
#    assign_unit(t, p)
#    assert t.name == 'DINPRO'
#    assert t.unit == 'dins'
#    
#
