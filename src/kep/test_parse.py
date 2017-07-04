# -*- coding: utf-8 -*-
"""
Testing status
==============
splitters.py - covered by doctests
cfg.py - requires some additinal testing/validation, see Tasks
parse.py: 

   test_parse.py           - testing strategy (this file)
                           - regression tests / bug fixes   

   test_parse_functions.py - stateless functions

   test_headers.py         - some classes with simple fixtures
                           - data pipleine, based on mock data  

   test_parse_by_datapoints.py - checks for actual testing results, 
                                 to be expanded along with cfg.py 
                                 definitions 

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

(2) Non-goals: 
    - 100% formal coverage by unit tests is not a target. Fixtures 
    for intermedaite results can grow very big and untransparent. 
    - Some tests in 'skeleton' (tst_draft.py) may remain empty.
 
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
"""

from pathlib import Path
import pytest
from tempfile import NamedTemporaryFile

import parse
import files
import splitter

# Testing dataflow with CSV-based fixtures and definitions    

@pytest.fixture
def _pdef():
    from cfg import Definition
    # WONTFIX: name MAIN is rather useless for Definition instance
    pdef = Definition("MAIN")
    pdef.add_header("Объем ВВП", "GDP")
    # WONTFIX: not testing boundaries here
    pdef.add_marker(None, None)
    pdef.require("GDP", "bln_rub")
    pdef.add_header("Индекс промышленного производства", "IND_PROD")
    pdef.require("IND_PROD", "yoy")
    return pdef

@pytest.fixture
def _units():
    # IDEA: may use explicit hardcoded constant with less units
    from cfg import UNITS
    return UNITS

def tab(values):
    return "\t".join(values)
assert tab(["1","2"]) == '1\t2'

def lines(*rows):
    return "\n".join([*rows])
assert lines("1","2") == '1\n2'

# headers:
JUNK_HEADER = lines(
    # skip empty rows
    "",    
    # skip comment
    "_____ Примечание",    
    # skip empty first cell
    "\t----this line will not be read ----")
    
SAMPLE_HEADER = lines(    
    # parse variable name 'GDP' from here
    "Объем ВВП" + "\t" * 4,
    # parse nothing from here, has "undefined lines" flag is raised
    "(уточненная оценка)",
    # parse unit 'bln_rub' form here
    "млрд.рублей" + "\t" * 4)   

SAMPLE_HEADER_2 = lines(
   '1.2. Индекс промышленного производства1) / Industrial Production index1)', 
   'в % к соответствующему периоду предыдущего года')

#rows:
sample_row_values = ["1991 1)", "4823", "901", "1102", "1373", "1447"]
sample_row_values_2 = ['2015', '99,2', '99,9', '98,3', '99,5', '99,1', '100,0', '98,2', '101,2', '98,2', '97,6', '99,1', '98,5', '100,2', '99,7', '98,4', '101,0', '98,1']

TABLE_TEXT = lines(JUNK_HEADER, SAMPLE_HEADER,   tab(sample_row_values))
TABLE_TEXT_2 = lines(           SAMPLE_HEADER_2, tab(sample_row_values_2))
CSV_TEXT =  lines(TABLE_TEXT, TABLE_TEXT_2)

class MockCSV():
    def __init__(self, contents):
        with NamedTemporaryFile('w') as f:
            self.path = f.name
        Path(self.path).write_text(contents, encoding='utf-8')
    def close(self):
        Path(self.path).unlink()

# using global constants, but avoids PermissionError problem, more stable
mock_csv = MockCSV(CSV_TEXT)
mock_csv_header = MockCSV(SAMPLE_HEADER)

# explicit teardown, more stable    
def  teardown_module():    
    mock_csv.close()
    mock_csv_header.close()

@pytest.fixture
def csv_path():
    return Path(mock_csv.path)

def test_csv_path_fixture_file_exists(csv_path):
    assert csv_path.exists()
    
def test_csv_path_fixture_file_content_equals_to_string(csv_path):
    assert CSV_TEXT == csv_path.read_text(encoding='utf-8')

@pytest.fixture
def csv_path_header():
    return Path(mock_csv_header.path)
    
# Info pipline:
# CSV -> Row() list -> RowStack() -> Tables -> Emitter -> Frames

## testing CSV -> Row() list

@pytest.fixture
def rows():
    path = Path(mock_csv.path)
    return list(parse.read_csv(path))

def test_read_csv_returns_row_instances(rows):    
    rows_dicts = [
 {'name': 'Объем ВВП', 'data': ['', '', '', '']},
 {'name': '(уточненная оценка)', 'data': []},
 {'name': 'млрд.рублей', 'data': ['', '', '', '']},
 {'name': '1991 1)', 'data': ['4823', '901', '1102', '1373', '1447']},
 {'name': '1.2. Индекс промышленного производства1) / Industrial Production index1)', 'data': []},
 {'name': 'в % к соответствующему периоду предыдущего года', 'data': []},
 {'name': '2015', 'data': ['99,2', '99,9', '98,3', '99,5', '99,1', '100,0', '98,2', '101,2', '98,2', '97,6', '99,1', '98,5', '100,2', '99,7', '98,4', '101,0', '98,1']}]
    assert len(rows) == len(rows_dicts) 
    assert rows[0].equals_dict(rows_dicts[0])
    for r, d in zip(rows, rows_dicts):
        assert r.equals_dict(d) is True


# Row() list -> RowStack()
# WONTFIX: not tested separately

# RowStack() -> Tables 
# WONTFIX: not tested separately


@pytest.fixture
def tables():
    rows = parse.read_csv(csv_path())
    return parse.get_tables_from_rows_segment(rows, _pdef(), _units())

@pytest.fixture
def table():
    return tables()[0]


class Test_Table():    

    def test_Table_instance_column_number(self, table):
        assert table.coln == 5

    def test_Table_instance_datarows(self, table):
        assert len(table.datarows) == 1
        assert table.datarows[0].name == '1991 1)'
        assert table.datarows[0].data == ["4823", "901", "1102", "1373", "1447"]        
        
    def test_Table_instance_has_defined_splitter_func(self, table):     
        assert table.splitter_func == splitter.split_row_by_year_and_qtr
                
    def test_Table_is_defined(self, table):
        assert table.is_defined() is True

    def test_Table_label_is_string(self, table):
        assert table.label == 'GDP_bln_rub'

    def test_Table_repr(self, table):
        assert table.__repr__() == 'Table GDP_bln_rub (headers: 3, datarows: 1)'

    def test_Table_str(self, table):
        print(table)
        assert table.__str__() == """Table GDP_bln_rub
columns: 5
varname: GDP, unit: bln_rub
+ <Объем ВВП>
- <(уточненная оценка)>
+ <млрд.рублей>
Row <1991 1) | 4823 901 1102 1373 1447>"""
    

# Table -> Emitter 
@pytest.fixture
def emitter(tables):    
    return parse.Emitter(table())

def test_emitter(emitter):
    a_91 = {'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1991}
    q1   = {'freq': 'q', 'label': 'GDP_bln_rub', 'qtr': 1, 'value': 901.0, 
            'year': 1991}
    assert emitter.a == [a_91]
    assert q1 in emitter.q
    assert emitter.m == []

# Tables -> DataPoints 
@pytest.fixture
def datapoints():    
    return parse.Datapoints(tables())

def test_datapoints(datapoints):
    z = {}    
    # gdp
    z[0] = {'year': 1991, 'label': 'GDP_bln_rub', 'freq': 'a', 'value': 4823.0}
    z[1] = {'year': 1991, 'label': 'GDP_bln_rub', 'freq': 'q', 'value': 1373, 
          'qtr': 3}   
    
    # ind_prod {'name': '2015', 'data': ['99,2', '99,9', '98,3', '99,5', '99,1', '100,0', '98,2', '101,2', '98,2', '97,6', '99,1', '98,5', '100,2', '99,7', '98,4', '101,0', '98,1']}]
    z[2] = {'freq': 'a', 'label': 'IND_PROD_yoy', 'value': 99.2, 'year': 2015}
    z[3] = {'freq': 'q', 'label': 'IND_PROD_yoy', 'value': 98.3, 'year': 2015, 
            'qtr': 2}
    z[4] = {'year': 2015, 'label': 'IND_PROD_yoy', 'freq': 'm', 'value': 98.1,
             'month': 12}
    for x in z.values():
        assert datapoints.includes(x)    
 

# DataPoints -> Frames
@pytest.fixture
def frames():
    return parse.Frames(tables())

def test_frames(frames):
    f = frames
    assert f.dfa['GDP_bln_rub'].sum() == f.dfq['GDP_bln_rub'].sum()
    # FIXME: test differently
    assert f.dfa['GDP_bln_rub'].sum() == 4823
    # FIXME: add IND_yoy
    
# regression tests - after bug fixes on occasional errors
def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

if __name__ == "__main__":
    pytest.main(["test_parse.py"])