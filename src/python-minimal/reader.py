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

    def __repr__(self):
        return f'Table(name={self.name}, unit={self.unit},\n    headers={self.headers},\n    datarows={self.datarows})'


def datarows_length(table):
    return max([len(row) for row in table.datarows])


def get_row_format(table, key=None):
    _key = key or datarows_length(table) - 1
    try:
        return {1 + 4 + 12: 'Y' + 'A' + 'Q' * 4 + 'M' * 12,
                1 + 4: 'Y' + 'A' + 'Q' * 4,
                1 + 12: 'Y' + 'A' + 'M' * 12,
                12: 'Y' + 'M' * 12,
                4: 'Y' + 'QQQQ',
                'fiscal': 'Y' + 'A' + 'M' * 11,
                }[_key]
    except KeyError:
        raise ValueError(f'Unknown row format for {table}')


def extract_unit(table, unit_mapper_dict):
    for row in table.headers:
        for text, unit in unit_mapper_dict.items():
            if text in row[0]:
                return unit
    return None


def emit_datapoints_from_row(row, label, row_format):
    # simplified version of extract.row_splitter()
    occurences = ''
    for value, letter in zip(row, row_format):
        occurences += letter
        if letter == 'Y':
            year = value
        if value and letter in 'AQM':
            yield dict(label=label,
                       freq=letter.lower(),
                       year=year,
                       period=occurences.count(letter),
                       value=value)


def emit_datapoints_from_table(table, label, row_format):
    for row in table.datarows:
        for d in emit_datapoints_from_row(row, label, row_format):
            yield d


def find_at_start(what: str, where: str):
    # FIXME: need test, currently doe snot look at start of words
    if re.search(pattern=f'{what}', string=where):
        return what
    return None


def find_tables(tables, strings, after=None):
    for t in tables:
        for string in strings:
            for row in t.headers:
                if find_at_start(string, row[0]):
                    yield t


def assert_single_table(table_subset):
    if len(table_subset) != 1:
        raise IndexError(f'Found multiple tables: {table_subset}')


def find_one_table(tables, header_string: str, after=None):
    table_subset = list(find_tables(tables, header_string, after))
    assert_single_table(table_subset)
    return table_subset[0]


def assign_units(tables, unit_mapper_dict):
    # inline assingment
    tables = list(tables)
    for i, table in enumerate(tables):
        tables[i].unit = extract_unit(table, unit_mapper_dict)


def make_label(name, unit):
    return f'{name}_{unit}'


def assert_unit_found(table, unit):
    if table.unit != unit:
        raise ValueError("Unit not found: {unit}")


def get_datapoints(tables, parsing_definition):
    table = find_one_table(tables, parsing_definition['headers'])
    assert_unit_found(table, parsing_definition['unit'])
    row_format = get_row_format(table, parsing_definition.get('reader'))
    label = make_label(parsing_definition['name'], table.unit)
    return emit_datapoints_from_table(table, label, row_format)


def to_values(filename, unit_mapper_dict, parsing_definitions):
    def unit_mapper(table):
        table.unit = extract_unit(table, unit_mapper_dict)
        return table
    csv_rows = read_csv("tab.csv")
    tables = split_to_tables(csv_rows)
    tables = list(map(unit_mapper, tables))
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
    # NOTES:
    #   - split_to_tables() is a state machine to traverse through csv file
    #   - in julia the data structure for Table class is likely to be different
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
