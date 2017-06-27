# -*- coding: utf-8 -*-
# TESTING INDIVIDUAL FUNCTIONS

import pandas as pd
from datetime import date

import pytest

import parse
import files

# risk areas: annual values, class of timestamps
class Test_DateFunctions():    
    
    def test_quarter_end_returns_pd_Timestamp(self):
        assert parse.get_date_quarter_end(2015, 1) == \
               pd.Timestamp('2015-03-31 00:00:00')
        assert parse.get_date_quarter_end(2015, 4) == \
               pd.Timestamp('2015-12-31 00:00:00')
        assert parse.get_date_quarter_end(2015, 4) == \
               pd.Timestamp(date(2015, 4*3, 1)) + pd.offsets.QuarterEnd()

    def test_month_end_returns_pd_Timestamp(self):
        assert parse.get_date_month_end(2015, 8) == \
               pd.Timestamp('2015-08-31 00:00:00')
        assert parse.get_date_month_end(2015, 1) == \
               pd.Timestamp(date(2015, 1, 1)) + pd.offsets.MonthEnd()

    def test_year_end_returns_pd_Timestamp(self):
        assert parse.get_date_year_end(2015) == pd.Timestamp('2015-12-31 00:00:00')
        assert parse.get_date_year_end(2015) == \
               pd.Timestamp(str(2015)) + pd.offsets.YearEnd()


# risk area: underscore as a separator may change
def test_labels_funcs():
    assert parse.extract_unit("GDP_mln_rub") == "mln_rub"
    assert parse.extract_varname("GDP_mln_rub") == "GDP"
    assert parse.split_label("GDP_mln_rub") == ("GDP", "mln_rub")
    assert parse.make_label("GDP", "mln_rub") == "GDP_mln_rub"


class Test_Function_to_float:
    # risk area: may be None instead of False
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert parse.to_float(x) is False

    def test_on_single_value(self):                                 
        assert parse.to_float('5.678,') == 5.678
        assert parse.to_float('5.678,,') == 5.678
        assert parse.to_float("5.6") == 5.6
        assert parse.to_float("5,6") == 5.6                     
        assert parse.to_float("5,67") == 5.67
        assert parse.to_float("5,67,") == 5.67
                             
    def test_on_comments(self):                                 
        assert parse.to_float('123,0 4561)') == 123
        assert parse.to_float('6762,31)2)') == 6762.3
        assert parse.to_float('1734.4 1788.42)') == 1734.4

    def all_values():
        # emit all values for debugging to_float()
        csv_path = files.get_path_csv()
        for table in parse.Tables(csv_path).get_all():
            for row in table.datarows:
                for value in row.data:
                    yield value


class Test_Function_get_year():
    
    def test_get_year(self):
        assert parse.get_year("19991)") == 1999
        assert parse.get_year("1999") == 1999
        assert parse.get_year("1812") is None
        
    def all_heads():
        # emit all heads for debugging get_year()
        csv_path = files.get_path_csv()
        csv_dicts = parse.read_csv(csv_path)
        for d in csv_dicts:
            yield d.name    

# -----------------------------------------------------------------------------

#FIXME: more testing for header
def test_Header():
    assert parse.Header.KNOWN != parse.Header.UNKNOWN

# -----------------------------------------------------------------------------

#FIXME: more testing for RowStack
def test_RowHolder_is_matched():
    foo = parse.RowStack.is_matched
    assert foo(pat="Объем ВВП", textline="Объем ВВП текущего года") is True
    assert foo(pat="Объем ВВП", textline="1.1 Объем ВВП") is False

# -----------------------------------------------------------------------------

header_row = parse.Row(['Объем ВВП', ''])
data_row = parse.Row(['1991', '10', '20', '30', '40'])

TABLE = parse.Table(headers=[header_row],
                    datarows=[data_row])

#TODO: can extract this information and check
TABLE.header.varname = 'GDP'
TABLE.header.unit = 'rog'

def test_Table_str():
    assert TABLE.__repr__() == 'Table GDP_rog (1 headers, 1 datarows)'


def test_Table_repr():
    assert TABLE.__str__() == """Table for variable GDP_rog
Number of columns: 4
varname: GDP, unit: rog
- <Объем ВВП>
------------------
1991 | 10 20 30 40
------------------"""

# -----------------------------------------------------------------------------

#TODO: more testing for Datapoints, Emitter, Frames
#      test repr and str's

# -----------------------------------------------------------------------------

def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

if __name__ == "__main__":
    pytest.main("test_parse.py")