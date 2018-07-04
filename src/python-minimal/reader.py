# Parse data from CSV files

# PSEUDOCODE
# ----------
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for reach table:
#   3.1. select variable label based on name and unit strings contained in table header
#   3.2. get data from table based on columns format like "YQQQQMMMMMMMMMMMM"
# 4. combine data from tables into three dataframes based on frequency (dfa, dfq, dfm)
# 5. write dfa, dfq, dfm as csv files to disk

# Full code code is at src/python/manage.py
# Point of entry of parsing algorithm:  src.python.dispatch.evaluate()


import csv
import re
from collections import OrderedDict
from enum import Enum, unique


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
    """Yield Table() instances from *rows* list of lists."""
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
    def __init__(self, headers, datarows, name=None, unit=None):
        self.headers = [x[0] for x in headers if x[0]]
        self.datarows = datarows
        self.name = name
        self.unit = unit
        self.row_format = get_row_format(self.coln)
        
    def __eq__(self, x):
        return str(self) == str(x)

    @property
    def label(self):
        return '{}_{}'.format(self.name, self.unit)
        
    @property
    def coln(self):
        return max([len(row) for row in self.datarows])        

    def is_defined(self):
        return self.name and self.unit 
    
    def headers_contain(self, string):
        for x in self.headers:
            if string in x:
                return True
        return False

#    def headers_search(self, string: str):
#        # FIXME: need test, currently doe snot look at start of words
#        for x in self.headers:
#            if re.search(pattern=string, string=x):
#                return string
#        return None

    def assign_row_format(self, key):
        self.row_format = get_row_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in emit_datapoints_from_row(row, _label, self.row_format):
                yield d
                
    def __repr__(self):
        return ',\n      '.join([f"Table(name='{self.name}'", 
                                f"unit='{self.unit}'",
                                f'headers={self.headers}',
                                f'datarows={self.datarows}'])

# row operations
    
ROW_FORMAT_DICT = {len(x): x for x in [
 'YAQQQQMMMMMMMMMMMM',
 'YAQQQQ',
 'YAMMMMMMMMMMMM',
 'YMMMMMMMMMMMM',
 'YQQQQ',
 'XXXX']}
ROW_FORMAT_DICT['fiscal'] = 'YA' + 'M' * 11

def get_row_format(key, row_format_dict=ROW_FORMAT_DICT):
    try:          
        return row_format_dict[key]
    except KeyError:
        raise ValueError(f'Unknown row format: {key}')

def emit_datapoints_from_row(row, label, row_format):
    occurences = ''
    for value, letter in zip(row, row_format):
        occurences += letter
        if letter == 'Y':
            year = value
        else:    
            if value:
                yield dict(label=label,
                           freq=letter.lower(),
                           year=year,
                           period=occurences.count(letter),
                           value=value)

# table operations

def get_tables(filename, unit_mapper_dict, parsing_definitions):
    def apply(x, funcs):
        for f in funcs:
            x = f(x)
        return x    
    unit_mapper = make_unit_mapper(unit_mapper_dict)
    name_mapper = make_name_mapper(parsing_definitions)
    changer = make_reader_changer(parsing_definitions)    
    tables = apply(filename, [read_csv,
                              split_to_tables,
                              lambda x: map(unit_mapper, x), 
                              lambda x: map(name_mapper, x),
                              list])
    # assign trailing variable names
    for pdef in parsing_definitions:
        _units = pdef['units'].copy()
        for prev_table, table in zip(tables[:-1], tables[1:]):
            if (table.name is None 
                and prev_table.name is not None
                and table.unit in _units):
                table.name = prev_table.name
                _units.remove(table.unit)                
    # end 
    return [changer(t) for t in tables if t.is_defined()]
    

def to_values(filename, unit_mapper_dict, parsing_definitions):
    tables = get_tables(filename, unit_mapper_dict, parsing_definitions)
    return [x for x in emit_datapoints(tables)]    


def emit_datapoints(tables):
    for table in tables:
        if table.unit and table.label:
            for x in table.emit_datapoints():
                yield x     


def complies(tables, parsing_definitions):
    pass                

# mappers

def make_unit_mapper(unit_mapper_dict):
    def mapper(table):
        for text, unit in unit_mapper_dict.items():
            if table.headers_contain(text):
               table.unit = unit
               break
        return table
    return mapper


def make_name_mapper(parsing_definitions):
    def mapper(table):
        for pdef in parsing_definitions:
            for line in pdef['headers']: 
                if table.headers_contain(line):
                     table.name = pdef['name']
                     break
        return table         
    return mapper                 


def make_reader_changer(parsing_definitions):
    pdefs = [pdef for pdef in parsing_definitions if pdef.get('reader')]
    def changer(table):
        for pdef in pdefs:
            if table.name == pdef['name']:
                key = pdef.get('reader')
                table.assign_row_format(key)
        return table
    return changer


if __name__ == "__main__":
    # simplified version of units.UNIT
    unit_mapper_dict = OrderedDict([
        ('млрд.рублей', 'bln_rub'),
        # this ...
        ('период с начала отчетного года в % к соответствующему периоду предыдущего года', 'ytd'),
        # ... must precede this
        ('в % к соответствующему периоду предыдущего года', 'yoy'),
        ('в % к предыдущему периоду', 'rog'),
        ('отчетный месяц в % к предыдущему месяцу', 'rog'),
    ])
    parsing_definition1 = dict(name='GDP',
                               headers=['Объем ВВП'],
                               units=['bln_rub'])
    unit_mapper = make_unit_mapper(unit_mapper_dict)
    name_mapper = make_name_mapper([parsing_definition1])
    # read csv
    csv_rows = list(read_csv("tab.csv"))
    # split csv rows to tables
    tables = list(split_to_tables(csv_rows))
    # assign units to all tables
    tables = list(map(unit_mapper, tables))
    assert tables[4].unit == 'ytd'    
    # apply defintions
    tables = list(map(name_mapper, tables))
    # extract
    tables = [t for t in tables if t.is_defined()]
    assert tables == get_tables('tab.csv', unit_mapper_dict, [parsing_definition1])

    # check result  of operations
    datapoints1 = [x for x in emit_datapoints(tables)]
    assert datapoints1[-1] == {'freq': 'q',
                               'label': 'GDP_bln_rub',
                               'period': 4,
                               'value': '25503',
                               'year': '20172)'}
    assert datapoints1[0] == {
        'freq': 'a',
        'label': 'GDP_bln_rub',
        'period': 1,
        'value': '4823',
        'year': '1999'}

    # full parsing cycle:
    filename = "tab.csv"
    gen = to_values(filename, unit_mapper_dict, [parsing_definition1])
    assert datapoints1 == gen

    # NOT TODO below

    # Special cases:
    # a) trailing tables eg find industrial production ytd from tables[4]
    pdef3 = dict(name='INDPRO',
                 headers=['Индекс промышленного производства'],
                 units=['yoy', 'rog', 'ytd'])
    tables = get_tables('tab.csv', unit_mapper_dict, [pdef3])
    assert [t.label for t in tables if t.is_defined()] == ['INDPRO_yoy', 'INDPRO_rog', 'INDPRO_ytd']  

    # b) sections - header found more than once in tables

    # c) duplicate tables - values appear in two sections

    # d) special reader fucntion for government budget indicators
    from pathlib import Path
    doc = """	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles
1999	653,8	22,7	49,2	91,5	138,7	185,0	240,0	288,5	345,5	400,6	454,0	528,0"""
    f = Path('temp.txt')
    f.write_text(doc, encoding='utf-8')
    parsing_definition2 = dict(headers=['Консолидированные бюджеты субъектов'],
                               name='VARX',
                               units=['bln_rub'],
                               reader='fiscal')
    data = to_values('temp.txt', unit_mapper_dict, [parsing_definition2])
    assert data[0] == {
        'freq': 'a',
        'label': 'VARX_bln_rub',
        'period': 1,
        'value': '653,8',
        'year': '1999'}
    assert data[-1] == {'freq': 'm', 'label': 'VARX_bln_rub',
                        'period': 11, 'value': '528,0', 'year': '1999'}
    f.unlink()
    
    # TODO:
    # - add real definitions
    # - add segmentations
    # - add defintions is fulfilled
    # - check a defintion against file (no duplicate values)