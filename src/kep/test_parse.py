# -*- coding: utf-8 -*-
"""
Testing status
==============
splitters.py - covered by doctests
cfg.py - requires some additinal testing/validation, see Tasks
parse.py - has two test suits:
   (1) test_parse.py - testing parts of algorithms using mock data
      - part 1 - stateless functions
      - part 2 - some classes with simple fixtures
      - part 3 - data pipleine, pased on mock data  
      - part 4 - regression tests / bug fixes   
   (2) test_parse_by_datapoints.py - checks for actual testing results, 
                                 to be expanded along with more variables in 
                                 cfg.py definitions 

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
    in 'skeleton' (tst_draft.py) may remain empty.
 
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
- what is the coverage tool to use? TODO: add from Misha's answer

- some useful tests died at https://github.com/epogrebnyak/data-rosstat-kep,
  summary of tests - which tests are potentially useful for mini-kep
 
test_parse.py 
-------------
 
- introduce skeleton from , mark tests to enhance and not-to-do tests

- complete fixtures list, sample csv must include at least two tables

- go to individual todo/fixme in tests 

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

from datetime import date
from tempfile import NamedTemporaryFile
from pathlib import Path
import pandas as pd

import pytest
from collections import OrderedDict as odict

import parse
import files
import splitter


# Part 1. Testing statless functions

# risk areas: annual values were not similar to other freq + class of timestamps
class Test_DateFunctions():
    def test_quarter_end_returns_pd_Timestamp(self):
        assert parse.get_date_quarter_end(2015, 1) == \
               pd.Timestamp('2015-03-31 00:00:00')
        assert parse.get_date_quarter_end(2015, 4) == \
               pd.Timestamp('2015-12-31 00:00:00')
        assert parse.get_date_quarter_end(2015, 4) == \
               pd.Timestamp(date(2015, 4 * 3, 1)) + pd.offsets.QuarterEnd()

    def test_month_end_returns_pd_Timestamp(self):
        assert parse.get_date_month_end(2015, 8) == \
               pd.Timestamp('2015-08-31 00:00:00')
        assert parse.get_date_month_end(2015, 1) == \
               pd.Timestamp(date(2015, 1, 1)) + pd.offsets.MonthEnd()

    def test_year_end_returns_pd_Timestamp(self):
        assert parse.get_date_year_end(2015) == pd.Timestamp('2015-12-31 00:00:00')
        assert parse.get_date_year_end(2015) == \
               pd.Timestamp('2015') + pd.offsets.YearEnd()


# risk area: underscore as a separator may change
def Test_Label_Handling_Functions():
    def test_multiple_functions(self):
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



# Part 2. Testing some classes (not all)

class Test_Header:
    
    def setup_method(self):
        self.header = gdp_table_header()
        
    def test_KNOWN_UNKNOWN_sanity(self):
        # risk area: this was actual error that happened
        assert parse.Header.KNOWN != parse.Header.UNKNOWN

    def test_creation(self):
        assert self.header.unit is None
        assert self.header.varname is None
        assert self.header.processed['Объем ВВП'] == parse.Header.UNKNOWN 
        assert self.header.processed['млрд.рублей'] == parse.Header.UNKNOWN 
        assert self.header.textlines == ['Объем ВВП', 'млрд.рублей', '1991 1)']

    def test_has_unknown_lines_after_creation(self):
        header = gdp_table_header()
        assert header.has_unknown_lines() is True

    def test_set_unit(self):
        header = gdp_table_header()
        assert header.unit is None
        assert header.processed['млрд.рублей'] == parse.Header.UNKNOWN
        header.set_unit(units())
        assert header.unit is not None
        assert header.processed['млрд.рублей'] == parse.Header.KNOWN

    def test_set_varname(self):
        header = gdp_table_header()
        assert header.varname is None
        header.set_varname(sample_pdef(), units())
        assert header.varname is not None

    def test_str(self):
        header = gdp_table_header()
        assert header.__str__() == 'varname: None, unit: None\n- <Объем ВВП>\n- <млрд.рублей>\n- <1991 1)>'


# -----------------------------------------------------------------------------

# FIXME: more testing for RowStack
def test_RowHolder_is_matched():
    foo = parse.RowStack.is_matched
    assert foo(pat="Объем ВВП", textline="Объем ВВП текущего года") is True
    assert foo(pat="Объем ВВП", textline="1.1 Объем ВВП") is False

# -----------------------------------------------------------------------------
class Test_Table_sample_gdp():
    
    def setup_method(self):
        self.table = sample_table_gdp()

    def test_Table_instance_column_number(self):
        assert self.table.coln == 17

    def test_Table_instance_datarows(self):
        assert len(self.table.datarows) == 1
        row = self.table.datarows[0]
        assert row.name == '1991 1)'
        assert row.data == ['100', '20', '20', '40', '40'] + ['10'] * 12
        
    def test_Table_instance_has_splitter_after_processing_pdef(self):     
        # """table.splitter_func"" is not None because table's """parse"" method has already been invoked (see sample_table_gdp())
        # TODO: change to specific splitter.* function
        assert self.table.splitter_func == splitter.split_row_by_periods     
                
    def test_Table_is_defined(self):
        assert self.table.is_defined() is True

    def test_Table_Header(self):
        header = self.table.header
        assert header.varname == 'GDP'
        assert header.unit == 'bln_rub'
        assert header.processed['Объем ВВП'] == parse.Header.KNOWN 
        assert header.processed['млрд.рублей'] == parse.Header.KNOWN 
        # we need do testlines?
        assert header.textlines == ['Объем ВВП', 'млрд.рублей']

    def test_Table_label(self):
        assert self.table.label == 'GDP_bln_rub'

    def test_Table_repr(self):
        assert self.table.__repr__() == 'Table GDP_bln_rub (headers: 2, datarows: 1)'

    def test_Table_str(self):
        assert self.table.__str__() == """Table GDP_bln_rub
columns: 17
varname: GDP, unit: bln_rub
+ <Объем ВВП>
+ <млрд.рублей>
<1991 1) | 100 20 20 40 40 10 10 10 10 10 10 10 10 10 10 10 10>"""


# Part 3. Sample data pipeline 

def get_temp_filename(contents):
    with NamedTemporaryFile('w') as f:
        # get path like C:\\Users\\EP\\AppData\\Local\\Temp\\tmp40stxmaj'
        filename = f.name
    # recreate file based on its bath - helps avoid PermissionError
    path = Path(filename)
    path.write_text(contents, encoding=parse.ENC)
    return path

# CSV text includes two variables and mock data for 1991
# not implemented / not todo: parts of program may fail if there is no values  
#                             at particular frequecy
# not implemented: testing for start end line markers 

CSV_TEXT = """Объем ВВП\t\t\t\t
млрд.рублей\t\t\t\t
\t----this line will be read ----

1991 1)\t100\t20\t20\t40\t40""" + "\t10" * 12 + \
"""\n
Индекс промышленного производства
в % к соответствующему периоду предыдущего года
1991\t103,2\t101,1\t102,2\t103,5\t104,9""" + \
"\t101,1" * 3 + "\t102,2" * 3 + "\t103,5" * 3 + "\t104,9" * 3


@pytest.fixture
def csv_path(text=CSV_TEXT):
    filename = get_temp_filename(text)
    yield filename
    # QUESTION: does next(csv_path()) take us here? is temp file deleted?
    Path(filename).unlink()


@pytest.fixture
def sample_rows():
    # FIXME: maybe generator is not consumed and temp file not deleted
    path = next(csv_path())
    return list(parse.read_csv(path))


@pytest.fixture
def sample_pdef():
    from cfg import Definition
    # WONTFIX: name MAIN is rather useless for Definition instance
    pdef = Definition("MAIN")
    pdef.add_header("Объем ВВП", "GDP")
    pdef.add_marker(None, None)
    pdef.require("GDP", "bln_rub")
    pdef.add_header("Индекс промышленного производства", "IND_PROD")
    pdef.require("IND_PROD", "yoy")
    return pdef


def units():
    from cfg import UNITS
    return UNITS


@pytest.fixture
def sample_tables():
    rows = sample_rows()
    return parse.get_tables_from_rows_segment(rows, sample_pdef(), units())


@pytest.fixture
def sample_table_gdp():
    return sample_tables()[0]


@pytest.fixture
def gdp_emitter():
    t = sample_tables()[0]
    return parse.Emitter(t)


@pytest.fixture
def sample_datapoints():
    tables = sample_tables()
    return parse.Datapoints(tables)


@pytest.fixture
def sample_frames():
    tables = sample_tables()
    dpoints = parse.Datapoints(tables)
    return parse.Frames(dpoints)


@pytest.fixture
def gdp_table_header():
    #FIXME: [:3] is volatile
    rows = sample_rows()[:3]
    return parse.Header(rows)

def test_read_csv(sample_rows):
    assert sample_rows.__repr__() == \
           "[<Объем ВВП>, " \
           "<млрд.рублей>, " \
           "<1991 1) | 100 20 20 40 40 10 10 10 10 10 10 10 10 10 10 10 10>, " \
           "<Индекс промышленного производства>, " \
           "<в % к соответствующему периоду предыдущего года>, " \
           "<1991 | 103,2 101,1 102,2 103,5 104,9 " \
           "101,1 101,1 101,1 102,2 102,2 102,2 103,5 103,5 103,5 104,9 104,9 104,9>]"


def test_table_gdp(sample_table_gdp):
    t = sample_table_gdp
    assert t.__str__() == """Table GDP_bln_rub
columns: 17
varname: GDP, unit: bln_rub
+ <Объем ВВП>
+ <млрд.рублей>
<1991 1) | 100 20 20 40 40 10 10 10 10 10 10 10 10 10 10 10 10>"""


def test_gdp_emitter(gdp_emitter):
    e = gdp_emitter
    assert e.emit_a() == [{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 100.0, 'year': 1991}]
    assert {'freq': 'q', 'label': 'GDP_bln_rub', 'qtr': 1, 'value': 20.0,
            'year': 1991} in e.emit_q()
    assert {'freq': 'm', 'label': 'GDP_bln_rub', 'month': 1, 'value': 10.0,
            'year': 1991} in e.emit_m()


def test_datapoints(sample_datapoints):
    pts = sample_datapoints
    assert pts.is_included({'freq': 'a', 'label': 'GDP_bln_rub', 'value': 100.0,
                            'year': 1991})
    assert pts.is_included({'freq': 'a', 'label': 'IND_PROD_yoy', 'value': 103.2,
                            'year': 1991})
    assert pts.is_included({'freq': 'q', 'label': 'GDP_bln_rub', 'qtr': 1,
                            'value': 20.0, 'year': 1991})
    assert pts.is_included({'freq': 'q', 'label': 'IND_PROD_yoy', 'qtr': 4,
                            'value': 104.9, 'year': 1991})
    assert pts.is_included({'freq': 'm', 'label': 'GDP_bln_rub', 'month': 1,
                            'value': 10.0, 'year': 1991})
    assert pts.is_included({'freq': 'm', 'label': 'IND_PROD_yoy', 'month': 12,
                            'value': 104.9, 'year': 1991})


def test_frames(sample_frames):
    f = sample_frames
    assert f.dfq.GDP_bln_rub.sum() == f.dfm.GDP_bln_rub.sum()
    assert f.dfa.GDP_bln_rub.sum() == 100
    # FIXME: add IND_yoy


# Part 4. Regression tests - after bug fixes on occasional errors

def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

if __name__ == "__main__":
    pytest.main(["test_parse.py"])