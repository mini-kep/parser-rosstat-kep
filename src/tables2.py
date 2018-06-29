"""Parse CSV text *csv_segment* using parsing definition *pdef*:

   evaluate(rows, pdef)
"""
from enum import Enum, unique
import re

import pandas as pd

from util.csv_reader import read_csv
from extract.to_float import to_float
from extract.row_splitter import get_splitter
from util.csv_reader import pop_rows
from inputs.instruction import yaml_to_instructions
from util.dataframe import create_dataframe
    

@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2

YEAR_CATCHER = re.compile("\D*(\d{4}).*")


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from *string* using *rx* regex.

       Returns:
           Year as integer
           False if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991 and year <= 2050:
            return year
    return False

def is_year(string: str) -> bool:
    return get_year(string) is not False


def split_to_tables(rows):
    """Yield Tab() instances from *rows* list of lists."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        # is data row?
        if is_year(row[0]):
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
    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows
        self.name = None
        self.unit = None
        key = self.count_columns(self.datarows)
        self.set_reader(key)
        
    def set_reader(self, reader=None):    
        if reader:
            self.splitter_func = get_splitter(reader)
            
    @property        
    def label(self):
        if self.name and self.unit:
            return self.name, self.unit
        return None
        
    @property
    def heads(self):
        return [x[0] for x in self.headers]        
    
    @staticmethod
    def count_columns(datarows):
         """Number of columns in table."""
         return max([len(row[1:]) for row in datarows]) 
        
    def make_datapoint(self, value: str, time_stamp, freq):
        return dict(label=(self.name, self.unit),                    
                    value=to_float(value),
                    time_index=time_stamp,
                    freq=freq)    
    
    def yield_values(self):
        """Yield dictionaries with variable name, frequency, time_index
           and value. May yield a dictionary where d['value'] is None.
        """
        for row in self.datarows:
            year = get_year(row[0])
            data = row[1:]
            a_value, q_values, m_values = self.splitter_func(data)
            if a_value:
                time_stamp = timestamp_annual(year)
                yield self.make_datapoint(a_value, time_stamp, 'a')
            if q_values:
                for t, val in enumerate(q_values):
                    time_stamp = timestamp_quarter(year, t + 1)
                    yield self.make_datapoint(val, time_stamp, 'q')
            if m_values:
                for t, val in enumerate(m_values):
                    time_stamp = timestamp_month(year, t + 1)
                    yield self.make_datapoint(val, time_stamp, 'm')    
        
    def __repr__(self):
        return str(self.__dict__)


def timestamp_annual(year):
    return pd.Timestamp(year, 12, 31)


def timestamp_quarter(year, quarter):
    month = quarter * 3
    return timestamp_month(year, month) # .date()


def timestamp_month(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()


def assign_trailing_units(tables, required):
    tables = list(tables)
    for prev_table, table in zip(tables, tables[1:]):
        if (table.name is None 
            and table.unit in required.get(prev_table.name,[])):
            table.name = prev_table.name
            
def yield_values(tables):
   for t in tables:
       if t.name and t.unit:
           for x in t.yield_values():
               yield x
               

def matches_at_start(x, pat):
    regex = r"\b{}".format(pat)
    return bool(re.search(regex, x))


def find(rows, patterns, comparison_func):
    return [pat
            for pat in patterns
            for row in rows
            if comparison_func(row, pat)]

def var_parser(headers, name):
    def _enclosed(table):
        if find(table.heads, headers, matches_at_start):
            table.name = name
        return table    
    return _enclosed


def unit_parser(units_ordered_dict):
    def _enclosed(table):
        for text, unit in units_ordered_dict.items():
            for row in table.heads:
                if text in row:
                    table.unit = unit
                    return table
        return table        
    return _enclosed


def includes_required(tables, required):
    req = [(name, unit) for name, units in required.items() for unit in units]    
    labs = [t.label for t in tables if t.label]
    diff = set(req) - set(labs)
    return diff == set()    


def render(csv_rows, unit_dict, headers_dict, required, reader):
    tables = split_to_tables(csv_rows)
    vparsers = [var_parser(headers, name) for name, headers in headers_dict.items()]
    uparser = unit_parser(unit_dict) 
    for parser in vparsers + [uparser]:
        tables = map(parser, tables)
    tables = list(tables)        
    assign_trailing_units(tables, required) 
    assert includes_required(tables, required)
    if reader:
        for t in tables:
            t.set_reader(reader)
    return tables    

def evaluate(csv_rows, definition, units):
    tables = render(csv_rows, 
                    units, 
                    pdef.headers_dict, 
                    pdef.required,
                    pdef.reader)
    for x in yield_values(tables):
        yield x
   
def split_to_segments(csv_text: str, yaml_doc):
    csv_rows = read_csv(csv_text)
    definitions = yaml_to_instructions(yaml_doc)
    segment_definitions = [d for d in definitions if d.boundaries]
    for pdef in segment_definitions:
        start, end = pdef.select_applicable_boundaries(csv_rows)
        csv_segment = pop_rows(csv_rows, start, end)
        yield csv_segment, pdef
    default_definition = [d for d in definitions if not  d.boundaries]     
    assert len(default_definition) == 1
    yield csv_rows, default_definition[0] 


def create_parser(units, yaml_doc):
    def _mapper(csv_text: str):
        for csv_rows, pdef in split_to_segments(csv_text, yaml_doc):
            tables = render(csv_rows, 
                            units, 
                            pdef.headers_dict, 
                            pdef.required,
                            pdef.reader)
            for value in yield_values(tables):
                yield value                    
    return _mapper
    

if __name__ == "__main__":  # pragma: no cover

    #test 1
    def make(csv_text: str):
        rows = read_csv(csv_text)
        return list(split_to_tables(rows))

    doc="""1.9. Ввод в действие жилых домов организациями всех форм собственности																	
    млн.кв.м общей площади																	
    1999	32,0	4,1	5,5	5,9	16,5	0,7	0,9	2,5	1,0	1,1	3,4	1,2	1,3	3,4	1,6	2,2	12,7
    2000	30,3	4,1	5,7	5,9	14,6	0,9	1,1	2,1	1,2	1,4	3,1	1,3	1,4	3,2	1,6	2,0	11,0    
    Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
    1999	4823	901	1102	1373	1447
    в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year
    1999	105,3	93,8	99,2	105,0	117,4	92,2	93,8	95,1	94,7	99,2	102,9	102,1	101,9	111,1	114,8	112,1	122,6
"""

    required1 = {'GDP': ['bln_rub', 'yoy'], 'DWELL': ['mln_m2']}     
    r1 = var_parser(name='GDP', headers=['Валовый внутренний продукт', 'Объем ВВП'])     
    r2 = var_parser(name='DWELL', headers=['Ввод в действие жилых домов организациями']) 
    u = unit_parser({'млрд.рублей': 'bln_rub',
                     'млн.кв.м общей площади': 'mln_m2',
                     '% к соответствующему периоду предыдущего года': 'yoy'})                       
    
    tables = make(doc)
    for x in [u, r1, r2]:
        tables = map(x, tables) 
    tables = list(tables)     
    assign_trailing_units(tables, required1)
    assert includes_required(tables, required1)
    for t in tables:
        t.set_reader()
    values = list(yield_values(tables))
    
    #test 2
    csv_rows = read_csv(doc)    
    tables2 = render(csv_rows, 
           unit_dict={'млрд.рублей': 'bln_rub',
                      'млн.кв.м общей площади': 'mln_m2',
                      '% к соответствующему периоду предыдущего года': 'yoy'},
           headers_dict={'GDP': ['Валовый внутренний продукт', 'Объем ВВП'],
                         'DWELL': ['Ввод в действие жилых домов организациями']},
           required={'GDP': ['bln_rub', 'yoy'], 'DWELL': ['mln_m2']},
           reader=None)
    values2=list(yield_values(tables2)) 
    assert values == values2
            

    # test 3
    DOC = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""
    tables = make(DOC)
    t = u(r1(tables[0]))
    datapoints = list(t.yield_values())
    assert datapoints[0] == {'freq': 'a',
                             'label': ('GDP', 'bln_rub'),
                             'time_index': pd.Timestamp('1999-12-31'),
                             'value': 4823}
    assert datapoints[1] == {'freq': 'q',
                             'label': ('GDP', 'bln_rub'),
                             'time_index': pd.Timestamp('1999-03-31'),
                             'value': 901}
    assert datapoints[2] == {'freq': 'q',
                             'label': ('GDP', 'bln_rub'),
                             'time_index': pd.Timestamp('1999-06-30'),
                             'value': 1102}
    assert datapoints[3] == {'freq': 'q',
                             'label': ('GDP', 'bln_rub'),
                             'time_index': pd.Timestamp('1999-09-30'),
                             'value': 1373}
    assert datapoints[4] == {'freq': 'q',
                             'label': ('GDP', 'bln_rub'),
                             'time_index': pd.Timestamp('1999-12-31'),
                             'value': 1447}
    

    from manage import Locations
    from inputs import UNITS, YAML_DOC, verify
    
    pdef = yaml_to_instructions(YAML_DOC)[0]
    loc = Locations(2018, 4)
    csv_text = loc.interim_csv.read_text(encoding='utf-8')
    _tables = render(read_csv(csv_text), 
                     UNITS, 
                     pdef.headers_dict, 
                     pdef.required,
                     pdef.reader)        
    values = list(create_parser(UNITS, YAML_DOC)(csv_text))
    dfs = {}
    for freq in 'aqm':
        df = create_dataframe(values, freq)
        dfs[freq] = df
        verify(df, freq) 
