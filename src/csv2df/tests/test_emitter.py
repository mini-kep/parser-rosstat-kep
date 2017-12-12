import pandas as pd
import io

import pytest

from csv2df.reader import Row
from csv2df.parser import Table
from csv2df.specification import ParsingCommand, Def
from csv2df.reader import to_rows
from csv2df.parser import extract_tables
import csv2df.emitter as emitter

# stateless functions

class Test_Function_to_float_on_values:
    # risk area: may be None instead of False, to discuss
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert emitter.to_float(x) is False

    def test_on_single_value_returns_float(self):
        assert emitter.to_float('5.678,') == 5.678
        assert emitter.to_float('5.678,,') == 5.678
        assert emitter.to_float("5.6") == 5.6
        assert emitter.to_float("5,6") == 5.6
        assert emitter.to_float("5,67") == 5.67
        assert emitter.to_float("5,67,") == 5.67

    def test_on_comments_returns_float(self):
        assert emitter.to_float('123,0 4561)') == 123
        assert emitter.to_float('6762,31)2)') == 6762.3
        assert emitter.to_float('1734.4 1788.42)') == 1734.4

    def test_on_max_recursion_depth_throws_exception(self):
        with pytest.raises(ValueError):
            emitter.to_float("1.2,,,,,")


def test_DatapointMaker():
    d = emitter.DatapointMaker('2000', 'abc')

    z = d.make('a', '100 1)2)')
    assert z['time_index'] == pd.Timestamp('2000-12-31')
    assert z["value"] == 100

    w = d.make('q', '25', 1)
    assert w['time_index'] == pd.Timestamp('2000-03-31')

    k = d.make('m', '6.55', 12)
    assert k['time_index'] == pd.Timestamp('2000-12-31')


labels = {0: 'GDP_bln_rub',
          1: 'GDP_rog',
          2: 'INDPRO_yoy'}

parsed_varnames = {0: 'GDP',
                   1: 'GDP',
                   2: 'INDPRO'}

parsed_units = {0: 'bln_rub',
                1: 'rog',
                2: 'yoy'}

headers = {0: [Row(['Объем ВВП', '', '', '', '']),
               Row(['млрд.рублей', '', '', '', ''])],
           1: [Row(['Индекс ВВП, в % к прошлому периоду/ GDP index, percent'])],
           2: [Row(['Индекс промышленного производства']),
               Row(['в % к соответствующему периоду предыдущего года'])]
           }

data_items = {0: [Row(["1991", "4823", "901", "1102", "1373", "1447"])],
              1: [Row(['1991', '106,4', '98,1', '103,1', '111,4', '112,0'])],
              2: [Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]
              }


class Sample:
    """Fixtures for testing"""
    def rows(i):
        return headers[i] + data_items[i]

    def headers(i):
        return headers[i]

    def data_items(i):
        return data_items[i]

    def table(i):
        return Table(headers[i], data_items[i])

    def table_parsed(i):
        t = Table(headers[i], data_items[i])
        t.varname = parsed_varnames[i]
        t.unit = parsed_units[i]
        t.set_splitter(reader=None)
        return t

    def label(i):
        return labels[i]

#-------------------------


def test_emitter():

    tables = [Sample.table_parsed(0), Sample.table_parsed(1)]
    e = emitter.Emitter(tables)
    dfq = e.get_dataframe('q')

    assert dfq.to_dict(orient='index') == {
        pd.Timestamp('1991-03-31'): {'GDP_bln_rub': 901.0,
                                     'GDP_rog': 98.1,
                                     'qtr': 1,
                                     'year': 1991},
        pd.Timestamp('1991-06-30'): {'GDP_bln_rub': 1102.0,
                                     'GDP_rog': 103.1,
                                     'qtr': 2,
                                     'year': 1991},
        pd.Timestamp('1991-09-30'): {'GDP_bln_rub': 1373.0,
                                     'GDP_rog': 111.4,
                                     'qtr': 3,
                                     'year': 1991},
        pd.Timestamp('1991-12-31'): {'GDP_bln_rub': 1447.0,
                                     'GDP_rog': 112.0,
                                     'qtr': 4,
                                     'year': 1991}}

    assert e.get_dataframe('a').to_dict(orient='index') == \
        {pd.Timestamp('1991-12-31'): {'GDP_bln_rub': 4823.0,
                                      'GDP_rog': 106.4,
                                      'year': 1991.0}}


# input data
csvfile1 = io.StringIO("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")

# input instruction
pc = ParsingCommand("GDP", "Объем ВВП", ["bln_rub"])
pdef = Def(pc, units=  {"млрд.рублей": "bln_rub"})

csv_segment = to_rows(csvfile1)
tables = extract_tables(csv_segment, pdef)
etr = emitter.Emitter(tables)
dfa = etr.get_dataframe(freq='a')
dfq = etr.get_dataframe(freq='q')
dfm = etr.get_dataframe(freq='m')


def test_resulting_dataframes():
    assert dfa.GDP_bln_rub['1999-12-31'] == 4823.0


def test_resulting_dataframes_with_time_index():
    assert dfq.to_dict('list') == {
        'year': [
            1999, 1999, 1999, 1999, 2000, 2000, 2000, 2000], 'qtr': [
            1, 2, 3, 4, 1, 2, 3, 4], 'GDP_bln_rub': [
                901.0, 1102.0, 1373.0, 1447.0, 1527.0, 1697.0, 2038.0, 2044.0]}


def test_resulting_dataframes_no_dfm():
    assert dfm.empty is True


if __name__ == "__main__":
    pytest.main([__file__])

    tables = [Sample.table_parsed(0), Sample.table_parsed(1)]
    e = emitter.Emitter(tables)
    dfa = e.get_dataframe('a')
