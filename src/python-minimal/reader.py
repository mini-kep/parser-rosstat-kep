# Parse data from CSV files


# This example is work in progress to create minimal example
# Full code code is at src/python/manage.py 
# Point of entry of parsing algorithm:  src.python.dispatch.evaluate() 


# PSEUDOCODE
# ---------- 
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for reach table:
#   3.1. select variable label based on name and unit strings contained in table header
#   3.2. get data from table based on columns format like "YQQQQMMMMMMMMMMMM"
# 4. combine data from tables into three dataframes based on frequency (dfa, dfq, dfm)
# 5. write dfa, dfq, dfm as csv files to disk 


# READ CSV AND SPLIT INTO TABLES (steps 1 and 2 of pseudocode)
# ------------------------------------------------------------

import csv
import re
from enum import Enum, unique

def read_csv(file): 
    """Read csv file as list of lists / matrix"""
    fmt=dict(delimiter='\t', lineterminator='\n')
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
        
    def __repr__(self):    
        return f'Table(headers={self.headers},\n       datarows={self.datarows}'



def emit_datapoints_from_row(row, label, row_format):
    # simplified version of extract.row_splitter()
    occurences = ''  
    for value, letter in zip(row, row_format):
       occurences += letter
       if letter=='Y':
           year = value
       else:       
           if value: 
                yield dict(label=label, 
                           freq=letter.lower(), 
                           year=year, 
                           period=occurences.count(letter),
                           value=value)

def emit_datapoints_from_table(table, label, row_format):
    for row in table.datarows:
        for d in emit_datapoints_from_row(row, label, row_format):
            yield d

# FIXME: need test, currently doe snot look at start of words
def find_at_start(what: str, where: str):
    if re.search(pattern=f'{what}', string=where):
         return what         
    return None 

def find_tables(tables, strings, after=None):
    for t in tables:
        for string in strings:
            for row in t.headers:            
                if find_at_start(string, row[0]):
                    yield t
                
def find_one_table(tables, header_string: str, after=None):               
    table_subset = list(find_tables(tables, header_string, after))
    if len(table_subset) != 1:
       raise IndexError(f'Found multiple tables: {table_subset}')
    return table_subset[0]
                
def extract_unit(table, unit_mapper):
    for row in table.headers:
        for text, unit in unit_mapper.items():                
            if text in row[0]:
                 return unit         
    return None        

def make_label(name, unit):
    return f'{name}_{unit}'
    
if __name__ == "__main__":
    # read csv    
    csv_rows = list(read_csv("tab.csv"))
    # split csv rows to tables
    # NOTES: 
    #   - split_to_tables() is a state machine to traverse through csv file 
    #   - in julia the data structure for Table class is likely to be different     
    tables = list(split_to_tables(csv_rows))
    
    # NOT TODO: simplest case a) both header and unit name are found in same table
    unit_mapper = {'млрд.рублей': 'bln_rub'}
    parsing_definition = dict(headers=['Объем ВВП'],
                              name='GDP',
                              unit='bln_rub',
                              row_format='YAQQQQ')
    table1 = find_one_table(tables, parsing_definition['headers'])
    unit = extract_unit(table1, unit_mapper)
    label = make_label(parsing_definition['name'], unit)
    datapoints = emit_datapoints_from_table(table1, 
                                            label, 
                                            parsing_definition['row_format'])    
    datapoints = list(datapoints)
    assert datapoints[-1] == {'freq': 'q',  'label': 'GDP_bln_rub',  'period': 4,  'value': '25503', 'year': '20172)'}
    assert datapoints[0] == {'freq': 'a',  'label': 'GDP_bln_rub', 'period': 1, 'value': '4823', 'year': '1999'}    
    # worse case b) find industrial production yoy from tables[4]
