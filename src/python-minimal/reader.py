# Parse data from CSV files

# Inputs: 
#  - csv file    
#  - text to unit mapping dictionary {'млрд.руб.': 'bln_rub'}
#  - variable name, text headers and units: 
#      {'name': 'INDPRO', 
#       'headers': ['Индекс промышленного производства'],  
#       'units': ['yoy', 'rog', 'ytd']}

# Output: list of dictionaries lile
#      {'freq': 'm', 
#       'label': 'INDPRO_rog', 
#       'year': '1999', 
#       'period': 11, 
#       'value': '104,3'}
    

# Pseudocode:
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for each table:
#   - identify unit of measurement    
#   - identify variable name    
#   - get values based on columns format "YQQQQMMMMMMMMMMMM"
# 4. combine data from tables into three dataframes based on frequency
#   - dfa (annual data)
#   - dfq (quarterly data)
#   - dfm (monthly data)
# 5. write dfa, dfq, dfm as CSV files to disk

# Full code code is at src/python/manage.py
# Point of entry of parsing algorithm:  src.python.dispatch.evaluate()


import csv
import re
from collections import OrderedDict
from enum import Enum, unique

# convert CSV to Table() instances

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


def split_to_tables(csv_rows):
    """Yield Table() instances from *csv_rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in csv_rows:
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


# Table class

def make_label(name, unit):
    return '{}_{}'.format(name, unit)    


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
        self.row_format = get_row_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in emit_datapoints_from_row(row, _label, self.row_format):
                yield d
                
    def __repr__(self):
        return ',\n      '.join([f"Table(name={repr(self.name)}", 
                                 f"unit={repr(self.unit)}",
                                 f"row_format={repr(self.row_format)}",
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

def emit_datapoints(tables):
    for table in tables:
        if table.unit and table.name:
            for x in table.emit_datapoints():
                yield x     

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
    
def import_tables(file):
    """Wraps read_csv() and split_to_tables() into one call."""
    return list(split_to_tables(read_csv(file)))
   
    
def parsed_tables(filename, unit_mapper_dict, namers):
    tables = import_tables(filename) 
    put_units(tables, unit_mapper_dict)
    put_names(tables, namers)
    put_readers(tables, namers)
    put_trailing_names_and_readers(tables, namers)
    return tables    

def to_values(filename, unit_mapper_dict, namers):
    tables = parsed_tables(filename, unit_mapper_dict, namers)
    return [x for x in emit_datapoints(tables)]



class Namer(object):    
    _ALWAYS_VALID_START_LINE = ''    
    def __init__(self, name, headers, units, 
                       starts=None, ends=None, reader=None):
        self.name = name
        self.headers = headers
        self.units = units
        if starts:
            self.starts = starts
        else:
            self.starts = [self._ALWAYS_VALID_START_LINE]            
        self.ends = ends
        self.reader = reader
        
    @property    
    def labels(self):
        return set(make_label(self.name, unit) for unit in self.units)
    
    def assert_all_labels_found(self, tables):
        diff = self.labels - {t.label for t in tables if t.is_defined()}
        if diff:
            raise ValueError(('Not found:', diff))
        
        
    def __repr__(self):    
        return str(self.__dict__)

if __name__ == "__main__":
    from parsing_definition import NAMERS, UNITS
    
#   Usual case - simple parsing:    
    # example 1
    unit_mapper_dict1 = OrderedDict([
        ('млрд.рублей', 'bln_rub'),
        # this ...
        ('период с начала отчетного года в % к соответствующему периоду предыдущего года', 'ytd'),
        # ... must precede this
        ('в % к соответствующему периоду предыдущего года', 'yoy'),
        ('в % к предыдущему периоду', 'rog'),
        ('отчетный месяц в % к предыдущему месяцу', 'rog'),
    ])
    namer1 = Namer(name='GDP', headers=['Объем ВВП'], units=['bln_rub'])
    filename = "tab.csv"
    tables = parsed_tables(filename,  
                           unit_mapper_dict=unit_mapper_dict1, 
                           namers=[namer1])
    assert tables[0].name == 'GDP'
    assert tables[0].unit == 'bln_rub'
    assert tables[0].row_format =='YAQQQQ'    
    assert tables[4].unit == 'ytd'
    datapoints1 = [x for x in emit_datapoints(tables)]
    assert datapoints1[94] == {'freq': 'q',
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

#    # example 2 - full parsing cycle
    assert datapoints1 == to_values(filename, unit_mapper_dict1, [namer1])

#    Special cases:
    
#    # example 3
#    # a) trailing tables eg find industrial production ytd from tables[4]
    namer3 = Namer(name='INDPRO',
                   headers=['Индекс промышленного производства'],
                    units=['yoy', 'rog', 'ytd'])
    tables3 = parsed_tables(filename,  
                           unit_mapper_dict=unit_mapper_dict1, 
                           namers=[namer3])
    assert [t.label for t in tables3 if t.is_defined()] == \
           ['INDPRO_yoy', 'INDPRO_rog', 'INDPRO_ytd']  
    datapoints3 = [x for x in emit_datapoints(tables3)]     
    assert datapoints3[148] == {'freq': 'm',
                                 'label': 'INDPRO_ytd',
                                 'period': 4,
                                 'value': '101,8', # checked at csv.txt
                                 'year': '2018'}
    assert datapoints3[0] == {'freq': 'a',
                                 'label': 'INDPRO_yoy',
                                 'period': 1,
                                 'value': '99,2', # checked at csv.txt
                                 'year': '2015'}
      

#    # example 4
#    # b) special reader fucntion for government budget indicators
    doc = """	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles
1999	653,8	22,7	49,2	91,5	138,7	185,0	240,0	288,5	345,5	400,6	454,0	528,0"""
    from pathlib import Path
    f = Path('temp.txt')
    f.write_text(doc, encoding='utf-8')
    namer4 = Namer(headers=['Консолидированные бюджеты субъектов'],
                   name='VARX',
                   units=['bln_rub'],
                   reader='fiscal')
    tables4 = parsed_tables(filename='temp.txt',  
                            unit_mapper_dict=unit_mapper_dict1, 
                            namers=[namer4])  
    f.unlink()
    datapoints4 = [x for x in emit_datapoints(tables4)]  
    assert datapoints4[11] == {'freq': 'm',
                               'label': 'VARX_bln_rub',
                               'period': 11,
                               'value': '528,0',
                               'year': '1999'}
    assert datapoints4[0] == {
                                'freq': 'a',
                                'label': 'VARX_bln_rub',
                                'period': 1,
                                'value': '653,8',
                                'year': '1999'}

# TODO
#    # example 5
#    # c) test for EXPORT/IMPORT improt with borders
    
#   regression test for bugsfix with 'млрд.тонно-км'    
    assert 'млрд.тонно-км' in '1.5. Грузооборот транспорта, включая коммерческий и некоммерческий грузооборот, млрд.тонно-км / Freight turnover, including commercial and noncommercial freight turnover, bln ton-km'
    text = '1.5. Грузооборот транспорта, включая коммерческий и некоммерческий грузооборот, млрд.тонно-км / Freight turnover, including commercial and noncommercial freight turnover, bln ton-km'
    row = [text, '', '']
    t = Table(headers=[row], datarows=[['100'] * 5])
    assert t.headers_contain('млрд.тонно-км')    
    assert 'млрд.тонно-км' in UNITS.keys()
    assert UNITS['млрд.тонно-км'] == 'bln_tkm'
    tables = [t]
    put_units(tables, UNITS)
    b = tables[0]
    assert b.unit=='bln_tkm'
    

    for namer in NAMERS:
        param = 'tab.csv', UNITS, [namer]
        tables = parsed_tables('tab.csv', UNITS, [namer])
        namer.assert_all_labels_found(tables)
        data = to_values(*param)
        print(namer.name)        
        for label in namer.labels:
            subdata = [x for x in data if x['label']==label]
            print(label)
            print(subdata[0])
            print(subdata[-1])
            #if label.startswith('TRANSPORT_LOADING_RAIL'):
            #    raise Exception             
    
# TODO:
#    - check a defintion against file (no duplicate values)    
#    - header found more than once in tables
#    - duplicate tables - values appear in two sections

