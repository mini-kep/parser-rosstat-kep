import pytest
import pandas as pd
from collections import OrderedDict as odict

from kep.csv2df.specification import Definition, Specification
from kep.csv2df.reader import text_to_list
from kep.csv2df.parser import split_to_tables, parse_tables, Table


DOC = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""


def create_table():
    rows = text_to_list(DOC)
    tables = list(split_to_tables(rows))
    return tables[0]


def test_split_to_tables():
    assert create_table() == \
        Table(headers=[['Объем ВВП, млрд.рублей / Gross domestic product, bln rubles']],
              datarows=[['1999', '4823', '901', '1102', '1373', '1447'],
                        ['2000', '7306', '1527', '1697', '2038', '2044']]
              )


class Test_Table():
    t = create_table()

    def test_extract_values_method_on_table_after_parsing_returns_expected_dicts(
            self):
        # prepare
        self.t.set_splitter(None)
        self.t.varname = 'GDP'
        self.t.unit = 'bln_rub'
        # run
        datapoints = list(self.t.extract_values())
        # compare
        assert datapoints[0] == {'freq': 'a',
                                 'label': 'GDP_bln_rub',
                                 'time_index': pd.Timestamp('1999-12-31'),
                                 'value': 4823}
        assert datapoints[1] == {'freq': 'q',
                                 'label': 'GDP_bln_rub',
                                 'time_index': pd.Timestamp('1999-03-31'),
                                 'value': 901}
        assert datapoints[2] == {'freq': 'q',
                                 'label': 'GDP_bln_rub',
                                 'time_index': pd.Timestamp('1999-06-30'),
                                 'value': 1102}
        assert datapoints[3] == {'freq': 'q',
                                 'label': 'GDP_bln_rub',
                                 'time_index': pd.Timestamp('1999-09-30'),
                                 'value': 1373}
        assert datapoints[4] == {'freq': 'q',
                                 'label': 'GDP_bln_rub',
                                 'time_index': pd.Timestamp('1999-12-31'),
                                 'value': 1447}


DOC2 = """	Год Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.
		I	II	III	IV
1.7. Инвестиции в основной капитал1), млрд. рублей / Fixed capital investments1), bln rubles
2015	14555,9	1969,7	3020,8	3560,2	6005,2	516,9	680,7	772,1	812,8	1004,2	1203,8	1078,4	1209,1	1272,7	1703,9	1592,7	2708,6
20162)		2149,4	3153,3	3813,4
	Год Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.
		I	II	III	IV
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year
2015	91,6	95,2	91,2	87,0	93,6	95,9	94,4	95,4	93,8	90,1	90,4	88,3	86,6	86,3	96,3	93,5	91,9
2016		95,2	96,1	100,3
в % к предыдущему периоду / percent of previous period
2015		35,2	152,1	108,9	160,4	20,7	129,1	116,4	104,2	123,0	118,2	87,8	105,3	103,6	134,3	92,9	163,0
2016		36,9	147,1	119,2
1.7.1. Инвестиции в основной капитал организаций"""


UNITS = odict([  # 1. MONEY
    ('млрд.рублей', 'bln_rub'),
    ('млрд. рублей', 'bln_rub'),
    # 2. RATES OF CHANGE
    ('в % к прошлому периоду', 'rog'),
    ('в % к предыдущему месяцу', 'rog'),
    ('в % к предыдущему периоду', 'rog'),
    ('в % к соответствующему периоду предыдущего года', 'yoy'),
    ('в % к соответствующему месяцу предыдущего года', 'yoy')
])


def make_definition():
    boundaries = [
        dict(start='1.6. Инвестиции в основной капитал',
             end='1.6.1. Инвестиции в основной капитал организаций'),
        dict(start='1.7. Инвестиции в основной капитал',
             end='1.7.1. Инвестиции в основной капитал организаций')]
    commands = [
        dict(
            var='INVESTMENT',
            header=['Инвестиции в основной капитал'],
            unit=['bln_rub', 'yoy', 'rog'])]
    # mapper dictionary to convert text in table headers to units of
    # measurement
    units = UNITS
    return Definition(commands, units, boundaries)


def create_tables():
    csv_segment = text_to_list(DOC2)
    return split_to_tables(csv_segment)


class Test_parse_tables:
    pdef = make_definition()
    tables = create_tables()

    def test_parse_tables(self):
        tables = parse_tables(self.tables, self.pdef)
        # checks
        assert len(tables) == 3
        assert all([t.has_unknown_lines() for t in tables]) is False
        for t in tables:
            assert t.varname == 'INVESTMENT'
        assert [t.unit for t in tables] == ['bln_rub', 'yoy', 'rog']


DOC3 = '\n'.join([DOC, DOC2])


def make_specification():
    commands = [
        dict(
            var='GDP',
            header='Объем ВВП',
            unit='bln_rub')]
    specification = Specification(commands=commands, units=UNITS)
    boundaries1 = [
        dict(start='1.6. Инвестиции в основной капитал',
             end='1.6.1. Инвестиции в основной капитал организаций'),
        dict(start='1.7. Инвестиции в основной капитал',
             end='1.7.1. Инвестиции в основной капитал организаций')]
    commands1 = [
        dict(
            var='INVESTMENT',
            header=['Инвестиции в основной капитал'],
            unit=['bln_rub', 'yoy', 'rog'])]
    specification.append(commands1, boundaries1)
    return specification


control_values = [
    {'freq': 'a', 'label': 'GDP_bln_rub',
     'time_index': pd.Timestamp('1999-12-31'),
     'value': 4823.0},
    {'freq': 'q',
     'label': 'GDP_bln_rub',
     'time_index': pd.Timestamp('2000-12-31'),
     'value': 2044.0},
    {'freq': 'a',
     'label': 'INVESTMENT_bln_rub',
     'time_index': pd.Timestamp('2015-12-31'),
     'value': 14555.9},
    {'freq': 'q',
     'label': 'INVESTMENT_rog',
     'time_index': pd.Timestamp('2016-09-30'),
     'value': 119.2}
]


def test_specification_with_2_segments_on_valid_csv_data():
    # setting
    spec = make_specification()
    spec.attach_data(DOC3)
    # call
    values = spec.values
    # check
    for d in control_values:
        assert d in values


if __name__ == "__main__":
    pytest.main([__file__])
