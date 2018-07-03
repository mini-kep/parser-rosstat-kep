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
    def __init__(self, headers, datarows):
        self.headers = [x[0] for x in headers]
        self.datarows = datarows
        self.name = None
        self.unit = None
        self.row_format = get_row_format(self.coln)

    @property
    def label(self):
        return '{}_{}'.format(self.name, self.unit)
        
    @property
    def coln(self):
        return max([len(row) for row in self.datarows])        

    def headers_contain(self, string):
        for x in self.headers:
            if string in x:
                return True
        return False

    def headers_search(self, string: str):
        # FIXME: need test, currently doe snot look at start of words
        for x in self.headers:
            if re.search(pattern=string, string=x):
                return string
        return None

    def assign_row_format(self, key):
        self.row_format = get_row_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in emit_datapoints_from_row(row, _label, self.row_format):
                yield d
                
    def __repr__(self):
        return f'Table(name={self.name}, unit={self.unit},\n    headers={self.headers},\n    datarows={self.datarows})'


def emit_datapoints(tables):
    for table in tables:
        if table.unit and table.label:
            for x in table.emit_datapoints():
                yield x                


row_formats = ['YA' + 'Q'*4 + 'M'*12,
               'YA' + 'Q'*4,
               'YA' + 'M'*12,
               'Y' + 'M'*12,
               'Y' + 'QQQQ',
               'XXXX']
row_format_dict = {len(x): x for x in row_formats}
row_format_dict['fiscal'] = 'YA' + 'M' * 11

def get_row_format(key, row_format_dict=row_format_dict):
    try:          
        return row_format_dict[key]
    except KeyError:
        raise ValueError(f'Unknown row format: {key}')


def extract_unit(table, unit_mapper_dict):
    for text, unit in unit_mapper_dict.items():
        if table.headers_contain(text):
           return unit
    return None


def emit_datapoints_from_row(row, label, row_format):
    # simplified version of extract.row_splitter()
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


def find_tables(tables, strings):
    return [t for t in tables for string in strings 
            if t.headers_contain(string)]


def assert_single_table(table_subset):
    if len(table_subset) != 1:
        raise IndexError(f'Found multiple tables: {table_subset}')


def find_one_table(tables, header_strings):
    table_subset = list(find_tables(tables, header_strings))
    assert_single_table(table_subset)
    return table_subset[0]


def assign_units(tables, unit_mapper_dict):
    # inline assingment
    tables = list(tables)
    for i, table in enumerate(tables):
        tables[i].unit = extract_unit(table, unit_mapper_dict)


def make_name_parser(parsing_definitions):
    def _(table):
        for pdef in parsing_definitions:
            for header in pdef['headers']: 
                if table.header_contains(header):
                     table.name = pdef['name']
        return table
    return _



def assert_correct_unit_found(table, unit):
    if table.unit != unit:
        raise ValueError("Unit not found: {unit}")


def get_datapoints(tables, parsing_definition):
    name = parsing_definition['name']
    table = find_one_table(tables, parsing_definition['headers'])
    table.name = name
    key = parsing_definition.get('reader')
    if key:
        table.assign_row_format(key)
    assert_correct_unit_found(table, parsing_definition['unit'])
    return table.emit_datapoints()


def to_values(filename, unit_mapper_dict, parsing_definitions):
    def unit_mapper(table):
        table.unit = extract_unit(table, unit_mapper_dict)
        return table    
    def name_mapper(table):
        for pdef in parsing_definitions:
            for header in pdef['headers']: 
                if table.headers_contain(header):
                     table.name = pdef['name']
        return table
    csv_rows = read_csv("tab.csv")
    tables = split_to_tables(csv_rows)
    tables = map(unit_mapper, tables)
    tables = map(name_mapper, tables)
    tables = list(tables)
    for pdef in parsing_definitions:
        for x in get_datapoints(tables, pdef):
            yield x


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

    def unit_mapper(table):
        table.unit = extract_unit(table, unit_mapper_dict)
        return table

    # read csv
    csv_rows = list(read_csv("tab.csv"))
    # split csv rows to tables
    tables = list(split_to_tables(csv_rows))
    # assign units to all tables
    assign_units(tables, unit_mapper_dict)
    assert tables[4].unit == 'ytd'

    # simplest case - both header and unit name are found in same table
    parsing_definition1 = dict(headers=['Объем ВВП'],
                               name='GDP',
                               unit='bln_rub')
    datapoints1 = get_datapoints(tables, parsing_definition1)

    # check result  of operations
    datapoints1 = list(datapoints1)
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
    assert datapoints1 == list(gen)

    # NOT TODO below

    # Special cases:
    # a) trailing tables eg find industrial production ytd from tables[4]
    itable1 = tables[2]  # this table has header for itable2
    itable2 = tables[4]  # this table has only unit

    # b) header found more than once in tables

    # c)- duplicate tables

    # d) special reader fucntion for government budget indicators
    from pathlib import Path
    doc = """	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles
1999	653,8	22,7	49,2	91,5	138,7	185,0	240,0	288,5	345,5	400,6	454,0	528,0"""
    f = Path('temp.txt')
    f.write_text(doc, encoding='utf-8')
    csv_rows = read_csv(str(f))
    tables_d = list(split_to_tables(csv_rows))
    assign_units(tables_d, unit_mapper_dict)
    parsing_definition2 = dict(headers=['Консолидированные бюджеты субъектов'],
                               name='VARX',
                               unit='bln_rub',
                               reader='fiscal')
    data = list(get_datapoints(tables_d, parsing_definition2))
    assert data[0] == {
        'freq': 'a',
        'label': 'VARX_bln_rub',
        'period': 1,
        'value': '653,8',
        'year': '1999'}
    assert data[-1] == {'freq': 'm', 'label': 'VARX_bln_rub',
                        'period': 11, 'value': '528,0', 'year': '1999'}
    f.unlink()