# -*- coding: utf-8 -*-
"""
Testing status
==============
splitters.py - covered by doctests
cfg.py - requires some additinal testing/validation, see Tasks
parse.py - has two test suits:
   test_parse.py - testing parts of algorithmusing mock data
   test_parse_by_datapoints.py - checks for actual testing results,
   will expand with along with cfg.py definitions expansion

Testing goals
=============
Tests should help to: 

    G.1 ensure we read all data we wanted (everything from parsing defnition 
        was read)
 
    G.2 this is actually the data requested (one table was not confused for 
        another)
 
    G.3 parts of algorithm return what is expected (helps to do refactoring, 
        once we change something in algorithm or data structures or else, 
        some tests break and we have to put in new ones)
 
    G.4 some functions return expected results on actual data (like to_float())


Test ideas
==========

(1) Some part of checks are implemented as validation procedures
    inside code, eg. check all required variables were read from csv

(2) Non-goal: 100% formal coverage by unit tests is not a target. Fixtures 
    for intermedaite results can grow very big and untransparent. Some tests
    in 'skeleton' may remain empty.    
 
(3) Must combine eye code review with unit tests and other types of tests. 

(4) Want to avoid too much testing of obvious easy-to test things. This will 
    not make this program better. 
    
(5) Testing provides ideas for refactoring - can leave comments about that. 

(6) Mentioning risk area in comments for the test is encouraged

(7) repr and str methds are used extensively, sometimes they retrun the same 
    in this program, repr is preferred

Tasks
======
    
general 
-------
- what is the coverage tool to use?

- some useful tests died at https://github.com/epogrebnyak/data-rosstat-kep
 
test_parse.py 
-------------
 
- introduce skeleton from , mark tests to enhance and not-to-do tests

- complete fixtures list, sample csv must include at least two tables


test_parse_by_datapoints.py
----------------------------

- change dataframe dumps constants when new parsing definitons are added in 
  cfg.py    
    
test_cfg.py 
-----------
- the algorithm will break if markers (start and end lines) are not in order
    
    to check for that:
      - must read csv file rows, use a reference csv file 
      - use first pair in start and end markers 
      - make sure the order of markers in specification is the same order as in 
        csv file
      - can be done as a test or as vaidator method
- Maybe a new name instead of 'markers', it has to be something 
     indicating the parsing definitoin boundary start and end line
"""
# TESTING INDIVIDUAL FUNCTIONS

import pandas as pd
from datetime import date

import pytest

import parse
import files
import splitter

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
    # risk area: may be None instead of False, to discuss
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert parse.to_float(x) is False

    def test_on_single_value_returns_float(self):                                 
        assert parse.to_float('5.678,') == 5.678
        assert parse.to_float('5.678,,') == 5.678
        assert parse.to_float("5.6") == 5.6
        assert parse.to_float("5,6") == 5.6
        assert parse.to_float("5,67") == 5.67
        assert parse.to_float("5,67,") == 5.67
                             
    def test_on_comments_returns_float(self):                                 
        assert parse.to_float('123,0 4561)') == 123
        assert parse.to_float('6762,31)2)') == 6762.3
        assert parse.to_float('1734.4 1788.42)') == 1734.4

    def all_values():
        """Emit all values for debugging to_float()"""
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
#TODO: make test Table class 
    
header_row = parse.Row(['Объем ВВП', ''])
data_row = parse.Row(['1991', '10', '20', '30', '40'])

TABLE = parse.Table(headers=[header_row],
                    datarows=[data_row])

#TODO: can extract this information and check
TABLE.header.varname = 'GDP'
TABLE.header.unit = 'rog'
TABLE.splitter_func = splitter.get_custom_splitter('fiscal')

def test_Table_repr():
    assert TABLE.__repr__() == 'Table GDP_rog (headers: 1, datarows: 1)'


def test_Table_str():
    assert TABLE.__str__() == """Table GDP_rog
columns: 4
varname: GDP, unit: rog
- <Объем ВВП>
<1991 | 10 20 30 40>"""

def test_Table_is_defined():
    assert TABLE.is_defined() is True

# -----------------------------------------------------------------------------

from tempfile import NamedTemporaryFile
from pathlib import Path

def get_temp_filename(contents: str):
    with NamedTemporaryFile('w') as f:
        # get path like C:\\Users\\EP\\AppData\\Local\\Temp\\tmp40stxmaj'
        filename = f.name
    #recreate file based on its bath - helps avoid PermissionError
    path = Path(filename)
    path.write_text(contents, encoding=parse.ENC)
    return path

CSV_TEXT = """Объем ВВП\t\t\t\t
млрд.рублей\t\t\t\t
\t
1991 1)\t100\t20\t20\t40\t40""" + "\t10" * 12

@pytest.fixture
def csv_path(text=CSV_TEXT):
    filename = get_temp_filename(text)
    yield filename
    Path(filename).unlink()

@pytest.fixture
def gdp_rows():
    #FIXME: maybe generator is not consumed and temp file not deleted
    path = next(csv_path())
    return list(parse.read_csv(path))

def pdef_gdp():
    from cfg import Definition
    pdef = Definition("MAIN")
    pdef.add_header("Объем ВВП", "GDP")
    pdef.add_marker(None, None)
    pdef.require("GDP", "bln_rub")
    return pdef

def units():
    from cfg import UNITS
    return UNITS

@pytest.fixture
def gdp_table():
    rows = gdp_rows()
    tables = parse.get_tables_from_rows_segment(rows, pdef_gdp(), units())
    return tables[0] 

@pytest.fixture
def gdp_emitter():
    t = gdp_table()
    return parse.Emitter(t)

@pytest.fixture
def gdp_frames():
    dpoints = parse.Datapoints([gdp_table()])
    return parse.Frames(dpoints)
  
def test_read_csv(gdp_rows):
    assert gdp_rows.__repr__() == \
    "[<Объем ВВП>, " \
    "<млрд.рублей>, "\
    "<1991 1) | 100 20 20 40 40 10 10 10 10 10 10 10 10 10 10 10 10>]"

def test_table(gdp_table):
    assert gdp_table.__str__() == """Table GDP_bln_rub
columns: 17
varname: GDP, unit: bln_rub
+ <Объем ВВП>
+ <млрд.рублей>
<1991 1) | 100 20 20 40 40 10 10 10 10 10 10 10 10 10 10 10 10>"""

def test_emitter(gdp_emitter):
    e = gdp_emitter
    assert e.emit_a() == [{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 100.0, 'year': 1991}]
    assert {'freq': 'q', 'label': 'GDP_bln_rub', 'qtr': 1, 'value': 20.0, 
            'year': 1991} in e.emit_q()
    assert {'freq': 'm', 'label': 'GDP_bln_rub', 'month': 1, 'value': 10.0,  
            'year': 1991} in e.emit_m() 

def test_datapoints(gdp_table):
    d = parse.Datapoints([gdp_table])
    assert d.is_included({'freq': 'a', 'label': 'GDP_bln_rub', 'value': 100.0, 'year': 1991})
    assert d.is_included({'freq': 'q', 'label': 'GDP_bln_rub', 'qtr': 1, 'value': 20.0, 'year': 1991})
    assert d.is_included({'freq': 'm', 'label': 'GDP_bln_rub', 'month': 1, 'value': 10.0,  'year': 1991})

def test_frames(gdp_frames):
    f = gdp_frames
    assert f.dfq.GDP_bln_rub.sum() == f.dfm.GDP_bln_rub.sum()
    assert f.dfa.GDP_bln_rub.sum() == 100
    
# testing on occasional errors
def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

if __name__ == "__main__":
    pytest.main(["test_parse.py"])