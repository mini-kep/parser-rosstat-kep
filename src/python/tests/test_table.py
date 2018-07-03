from collections import OrderedDict

import pandas as pd
import pytest
from dispatch import (
    Table,
    timestamp_quarter,
    timestamp_month,
    timestamp_annual)
from extract.row_splitter import split_row_by_year_and_qtr, split_row_fiscal


@pytest.fixture
def table():
    headers = [['Объем ВВП', '', '', '', ''],
               ['млрд.рублей', '', '', '', '']]
    datarows = [['1991', '4823', '901', '1102', '1373', '1447']]
    return Table(headers, datarows)


@pytest.fixture
def parsed_table():
    t = table()
    t.name = 'GDP'
    t.unit = 'bln_rub'
    return t


class Test_Table:

    def test_on_creation_pasring_attributes_are_unknown(self, table):
        assert table.label is None
        assert table.heads == ['Объем ВВП', 'млрд.рублей']
        assert table.name is None
        assert table.unit is None

    def test_str_repr(self, table):
        assert str(table)

    def test_set_splitter(self, table):
        assert table.splitter_func == split_row_by_year_and_qtr
        table.set_reader('fiscal')
        assert table.splitter_func == split_row_fiscal

    def test_yeild_values_on_parsed_table(self, parsed_table):
        values = list(parsed_table.yield_values())
        assert len(values) == 5
        assert values[0] == {'label': ('GDP', 'bln_rub'),
                             'value': 4823.0,
                             'time_index': pd.Timestamp('1991-12-31'),
                             'freq': 'a'}
        assert values[4] == {'label': ('GDP', 'bln_rub'),
                             'value': 1447.0,
                             'time_index': pd.Timestamp('1991-12-31'),
                             'freq': 'q'}


def test_timestamp_quarter():
    assert timestamp_quarter(1999, 1) == pd.Timestamp('1999-03-31')


def test_timestamp_month():
    assert timestamp_month(1999, 1) == pd.Timestamp('1999-01-31')


def test_timestamp_annual():
    assert timestamp_annual(1999) == pd.Timestamp('1999-12-31')


if __name__ == "__main__":
    pytest.main([__file__])
