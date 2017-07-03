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

import pytest

import parse
import files



# Part 2. Testing some classes (not all)

# Many classes moved to test_header.py

# TODO: more to Rows test
#def test_RowStack_is_matched():
#    foo = parse.RowStack.is_matched
#    assert foo(pat="Объем ВВП", textline="Объем ВВП текущего года") is True
#    assert foo(pat="Объем ВВП", textline="1.1 Объем ВВП") is False

ROWS = [{'name': 'Объем ВВП', 'data': ['', '', '', '']},
 {'name': '(уточненная оценка)', 'data': []},
 {'name': 'млрд.рублей', 'data': ['', '', '', '']},
 {'name': '1991 1)', 'data': ['100', '20', '30', '40', '10']},
 {'name': 'Индекс промышленного производства', 'data': []},
 {'name': 'в % к соответствующему периоду предыдущего года', 'data': []},
 {'name': '1991', 'data': ['102,7', '101,1', '102,2', '103,3', '104,3', '101,1', '101,1', '101,1', '102,2', '102,2', '102,2', '103,3', '103,3', '103,3', '104,3', '104,3', '104,3']}]

def to_row(d):
    return parse.Row([d['name']] + d['data'])
    
@pytest.fixture
def row_stack():    
    rows = [to_row(d) for d in ROWS]
    return parse.RowStack(rows)

@pytest.fixture
def pdef2():
    from cfg import Definition
    pdef = Definition("MAIN")
    pdef.add_header("Объем ВВП", "GDP")
    #parsing defintion with none markers
    pdef.add_marker(None, None)
    return pdef

def test_row_stack_fixture_self_test(row_stack):
    for s, r in zip(row_stack.rows, ROWS):
        assert s.name == r['name']
        assert s.data == r['data']

class Test_RowStack_stable_on_definition_with_None_markers:
    
    def test_pop_returns_segment(self, row_stack, pdef2):
        csv_segment = row_stack.pop(pdef2)
        assert len(csv_segment) == 7
    
    def test_is_found_raises_error(self, row_stack):
        with pytest.raises(AttributeError):
            # error found in Rows
            row_stack.is_found(None)

# Part 4. Regression tests - after bug fixes on occasional errors

def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

if __name__ == "__main__":
    pytest.main(["test_parse.py"])