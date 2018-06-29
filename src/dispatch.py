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
from inputs.instruction import InstructionSet

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
               

def var_parser(headers, name):
    def _enclosed(table):
        for pat in headers:
            regex = re.compile(r"\b{}".format(pat))
            for x in table.heads:
                if bool(re.search(regex, x)):
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


def _render(csv_rows, unit_dict, headers_dict, required, reader):
    tables = split_to_tables(csv_rows)
    vparsers = [var_parser(headers, name) for name, headers in headers_dict.items()]
    uparser = unit_parser(unit_dict) 
    for parser in vparsers + [uparser]:
        tables = map(parser, tables)
    tables = list(tables)        
    assign_trailing_units(tables, required) 
    if reader:
        for t in tables:
            t.set_reader(reader)
    return tables    


def render(csv_rows, unit_dict, headers_dict, required, reader):
    tables = _render(csv_rows, unit_dict, headers_dict, required, reader)
    try:
        req = [(name, unit) for name, units in required.items() for unit in units]    
        labs = [t.label for t in tables if t.label]
        diff = set(req) - set(labs)
        assert diff == set()  
    except AssertionError:
        raise AssertionError((diff, headers_dict)) 
    return tables    

  
def split_to_segments(csv_text: str, yaml_doc):
    csv_rows = read_csv(csv_text)
    segment_definitions = InstructionSet(yaml_doc).by_segment
    for pdef in segment_definitions:
        start, end = pdef.select_applicable_boundaries(csv_rows)
        csv_segment = pop_rows(csv_rows, start, end)
        yield csv_segment, pdef
    yield csv_rows, InstructionSet(yaml_doc).default


def evaluate(csv_text: str, units: dict, yaml_doc: str):
    for csv_rows, pdef in split_to_segments(csv_text, yaml_doc):
        tables = render(csv_rows, 
                        units, 
                        pdef.headers_dict, 
                        pdef.required,
                        pdef.reader)
        for value in yield_values(tables):
            yield value     
    

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
    
    # test 4
    from manage import Locations
    from inputs import UNITS, YAML_DOC, verify
    from util.dataframe import create_dataframe
    
    pdef = InstructionSet(YAML_DOC).default
    loc = Locations(2010, 1)
    csv_text = loc.interim_csv.read_text(encoding='utf-8')
    _tables = _render(read_csv(csv_text), 
                     UNITS, 
                     pdef.headers_dict, 
                     pdef.required,
                     pdef.reader)        
    values = list(evaluate(csv_text, UNITS, YAML_DOC))
    dfs = {}
    for freq in 'aqm':
        df = create_dataframe(values, freq)
        dfs[freq] = df
        verify(df, freq) 


    # example must be able to parse a unit far away from original name
    doc = """	Год 1)	Кварталы 1)	Январь	Февраль	Март	Апрель	Май	Июнь	Июль	Август	Сен- тябрь	Октябрь	Ноябрь	Декабрь			
		I	II	III	IV												
4.1.2. Общая численность безработных, на конец месяца 2)																	
млн.человек																	
1999	9,4	10,2	9,4	8,9	9,1	10,1	10,5	10,1	9,7	9,3	9,1	9,0	8,8	8,9	9,0	9,2	9,1
2000	7,7	8,8	7,7	7,2	7,1	9,0	9,0	8,5	8,0	7,6	7,5	7,3	7,2	7,1	7,1	7,1	7,1
2001	6,4	7,0	6,2	6,2	6,2	7,1	7,1	6,8	6,5	6,1	6,1	6,1	6,1	6,2	6,2	6,3	6,2
2002	5,8	6,0	5,6	5,5	6,3	6,1	6,0	5,9	5,7	5,6	5,5	5,4	5,3	5,7	6,0	6,3	6,5
2003	6,2	6,7	6,2	6,0	6,1	6,6	6,8	6,6	6,3	6,1	6,0	6,0	6,0	6,0	6,0	6,0	6,3
2004	6,0	6,7	5,7	5,5	6,1	6,6	6,9	6,5	6,0	5,6	5,5	5,5	5,4	5,7	5,9	6,1	6,1
2005	5,6	6,0	5,5	5,4	5,5	6,1	6,0	5,8	5,6	5,4	5,4	5,4	5,4	5,4	5,5	5,5	5,7
2006	5,3	5,7	5,5	5,0	5,0	5,7	5,8	5,7	5,6	5,6	5,3	5,1	4,9	4,9	5,0	5,0	5,1
2007	4,6	5,2	4,5	4,3	4,4	5,3	5,4	5,1	4,8	4,5	4,4	4,3	4,3	4,3	4,3	4,2	4,6
2008	4,8	5,1	4,3	4,4	5,4	5,0	5,3	4,9	4,5	4,1	4,2	4,3	4,5	4,7	5,0	5,3	5,9
2009	6,3	6,8	6,5	6,0	6,1	6,5	7,1	6,9	6,7	6,5	6,3	6,2	6,0	5,8	5,9	6,2	6,2
2010		6,6	5,6			6,8	6,4	6,4	6,1	5,6	5,2						
_____________________ 1) В среднем за год, за квартал. 2) С января 2002г. по октябрь 2005г. с учетом численности официально зарегистрированных безработных по Чеченской Республике. С ноября 2005г. с учетом численности безработных по данным выборочных обследований населения по проблемам занятости в Чеченской Республике.																	
	Год 1)	Кварталы 1)	Январь	Февраль	Март	Апрель	Май	Июнь	Июль	Август	Сен- тябрь	Октябрь	Ноябрь	Декабрь			
		I	II	III	IV												
в % к соответствующему периоду предыдущего года2)																	
1999	116,0	128,9	121,9	119	97,6	126,1	132,1	128,4	124,7	121	119,9	118,9	117,8	120,5	101,2	98,3	93,7
2000	82,0	86,4	81,8	81,3	77,9	89,5	85,6	84,2	82,8	81,2	81,5	81,7	82,0	80,3	78,7	77,1	78,0
2001	83,2	79,6	81,3	84,9	88,0	78,9	79,8	80,2	80,6	81,1	82,3	83,6	84,9	86,3	87,7	89,1	87,1
2002	89,2	84,6	90,6	86,6	97,8	85,2	83,3	85,3	87,5	89,9	88,0	86,2	84,4	89,0	93,5	97,9	102,0
2003	107,3	111,1	109,8	110,6	97,3	108,7	113,1	111,7	110,1	108,6	110,6	112,1	113,6	106,4	100,3	94,7	97,1
2004	96,1	100,0	93,1	91,6	99,1	99,5	101,7	98,8	95,4	91,8	91,9	90,7	90,0	94,2	98,3	102,4	96,9
2005	93,7	89,7	95,8	98,1	92,0	91,9	87,5	89,9	93,1	96,8	97,7	98,8	99,5	96,0	93,1	90,3	92,6
2006	94,9	97,2	101,0	91,6	91,2	95,0	97,3	99,3	101,1	103,1	98,9	94,6	90,3	90,0	89,7	91,2	91,8
2007	86,7	91,5	82,6	85,6	86,7	92,5	93,1	89,0	84,9	80,6	82,4	84,4	86,5	86,0	85,5	84,9	89,7
2008	104,4	96,5	94,2	105,6	123,7	94,2	98,5	96,6	94,4	91,9	96,1	100,4	104,9	111,4	118,0	124,6	128,2
2009	131,7	134,8	152,1	132,2	112,3	131,2	132,9	140,4	148,6	158,2	149,8	141,8	134,3	121,5	116,9	116,5	104,7
2010		96,3	86,7			105,1	91,2	93,2	91,8	85,7	82,3						
в % к экономически активному населению																	
1999	13,0	14,3	13,0	12,3	12,5	14,3	14,6	14,0	13,5	12,9	12,8	12,5	12,1	12,2	12,4	12,6	12,5
2000	10,5	12,1	10,4	9,9	9,8	12,5	12,4	11,4	10,8	10,3	10,1	10,0	9,9	9,8	9,8	9,8	9,9
2001	9,0	9,8	8,7	8,5	8,7	9,9	10,0	9,5	9,1	8,6	8,5	8,5	8,5	8,6	8,7	8,8	8,6
2002	8,0	8,4	7,7	7,4	8,6	8,5	8,4	8,2	8,0	7,7	7,5	7,4	7,2	7,7	8,2	8,7	9,0
2003	8,6	9,3	8,5	8,2	8,3	9,2	9,5	9,2	8,8	8,4	8,4	8,3	8,2	8,2	8,2	8,2	8,6
2004	8,2	9,2	7,8	7,5	8,2	9,1	9,5	8,9	8,2	7,6	7,5	7,4	7,3	7,7	8,0	8,4	8,3
2005	7,6	8,2	7,4	7,3	7,5	8,3	8,3	8,0	7,6	7,3	7,3	7,3	7,2	7,3	7,4	7,5	7,6
2006	7,2	7,8	7,4	6,7	6,8	7,8	7,9	7,7	7,6	7,5	7,2	6,8	6,5	6,6	6,7	6,7	6,9
2007	6,1	7,0	6,0	5,7	5,8	7,1	7,2	6,8	6,4	5,9	5,8	5,7	5,6	5,6	5,6	5,7	6,1
2008	6,4	6,7	5,6	5,9	7,1	6,6	7,1	6,5	6,0	5,4	5,6	5,7	5,8	6,2	6,6	7,0	7,8
2009	8,4	9,1	8,6	7,8	8,0	8,7	9,4	9,2	8,8	8,5	8,3	8,1	7,8	7,6	7,7	8,2	8,2
2010		8,8	7,4			9,2	8,6	8,6	8,2	7,3	6,8"""

    t2 = _render(read_csv(doc), 
                     UNITS, 
                     pdef.headers_dict, 
                     pdef.required,
                     pdef.reader) 

