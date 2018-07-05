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
#       'date': '1999-12-31',
#       'value': '104,3'}
#
#
# Pseudocode
#
# reader.py:    
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for each table:
#   - identify unit of measurement
#   - identify variable name
#   - get values based on columns format like "YQQQQMMMMMMMMMMMM"
# saver.py:
# 4. combine data from tables into three dataframes based on frequency
#   - dfa (annual data)
#   - dfq (quarterly data)
#   - dfm (monthly data)
# 5. write dfa, dfq, dfm as CSV files to disk

# Full code code is at src/python/manage.py
# Point of entry of parsing algorithm:  src.python.dispatch.evaluate()


import csv
from datetime import date
from collections import OrderedDict
from enum import Enum, unique
import calendar

import filters

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


MONTHS = dict(a=12, q=3, m=1)


def timestamp(year: str, period: int, freq: str):
    year = filters.clean_year(year)
    month = MONTHS[freq] * period
    day = calendar.monthrange(year, month)[1]
    return f'{year}-{str(month).zfill(2)}-{day}'


def emit_datapoints_from_row(row, label, row_format):
    occurences = ''
    for value, letter in zip(row, row_format):
        occurences += letter
        if letter == 'Y':
            year = value
        else:
            if value:
                period = occurences.count(letter)
                freq = letter.lower()
                yield dict(label=label,
                           freq=freq,
                           date=timestamp(year, period, freq),
                           value=filters.clean_value(value))


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


if __name__ == "__main__":
    from parsing_definition import NAMERS, UNITS, Namer
    from dev_helper import PATH

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
    filename = PATH
    tables = parsed_tables(filename,
                           unit_mapper_dict=unit_mapper_dict1,
                           namers=[namer1])
    assert tables[0].name == 'GDP'
    assert tables[0].unit == 'bln_rub'
    assert tables[0].row_format == 'YAQQQQ'
    assert tables[4].unit == 'ytd'
    datapoints1 = [x for x in emit_datapoints(tables)]
    assert datapoints1[94] == {'freq': 'q',
                               'label': 'GDP_bln_rub',
                               'date': date(2017, 12, 31),
                               'value': 25503}
    assert datapoints1[0] == {
        'freq': 'a',
        'label': 'GDP_bln_rub',
        'date': date(1999, 12, 31),
        'value': 4823}

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
                                'date': date(2018, 4, 30),
                                'value': 101.8  # checked at csv.txt
                                }
    assert datapoints3[0] == {'freq': 'a',
                              'label': 'INDPRO_yoy',
                              'date': date(2015, 12, 31),
                              'value': 99.2  # checked at csv.txt
                              }


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
                               'date': date(1999, 11, 30),
                               'value': 528.0}
    assert datapoints4[0] == {
        'freq': 'a',
        'label': 'VARX_bln_rub',
        'date': date(1999, 12, 31),
        'value': 653.8}

#    # example 5
#    # c) test for EXPORT/IMPORT improt with borders
    namer5 = Namer(
        name='EXPORT_GOODS',
        headers=[
            'экспорт товаров – всего',
            'Экспорт товаров'],
        units=['bln_usd'],
        starts=[
            "1.9. Внешнеторговый оборот – всего",
            "1.10. Внешнеторговый оборот – всего",
            "1.10. Внешнеторговый оборот – всего"],
        ends=[
            "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья",
            "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья",
            "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья"])
    tables5 = parsed_tables(filename,
                            unit_mapper_dict=UNITS,
                            namers=[namer5])
    datapoints5 = [x for x in emit_datapoints(tables5)]
    assert datapoints5[0]['value'] == 75.6
    """1.9. Внешнеторговый оборот – всего1), млрд.долларов США / Foreign trade turnover – total1), bln US dollars

	Год Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.
		I	II	III	IV
в том числе:
экспорт товаров – всего, млрд.долларов США
/ of which: export of goods – total, bln US dollars
1999	75,6	15,3	17,1	18,9	24,3	4,5	4,9	5,8	6,6	5,1	5,4	6,3	6,2	6,4	7,0	7,6	9,7"""


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
    assert b.unit == 'bln_tkm'

    expected_values = []
    for namer in NAMERS:
        param = PATH, UNITS, [namer]
        tables = parsed_tables(*param)
        namer.assert_all_labels_found(tables)
        data = to_values(*param)
        print(namer.name)
        for label in namer.labels:
            subdata = [x for x in data if x['label'] == label]
            a, z = subdata[0], subdata[-1]
            print(label)
            print(a)
            expected_values.append(a)
            print(z)
            expected_values.append(z)
    import yaml
    Path('checkpoints.yaml').write_text(yaml.dump(expected_values))

# WIP:
#  - full new defintion of parsing_defintion.py
#  - write expected values

# TODO - OTHER:
#  - convert to tests
#  - timeit
#  - datapoint checks
#  - checking dataframes

# WONTFIX:
#  - saving to dataframes
#  - testing on tab.csv and tab_old.csv
#  - clean notebook folders
#  - check a defintion against file (no duplicate values) - Namer.inspect()
#  - header found more than once in tables
#  - duplicate tables - values appear in two sections, eg CPI
#  - maybe handle 'reader' directly
#  - 1.7. Объем работ по виду деятельности ""Строительство - requires supress_apos()

# DONE
#  - type conversions and comment cleaning
#  - assert schema on namer imports
