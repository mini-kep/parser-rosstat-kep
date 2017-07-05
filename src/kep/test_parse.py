# -*- coding: utf-8 -*-
"""
Testing/validation goals
========================
G.1 ensure we read all data we specified in parsing defnition 

G.2 this is actually the data requested (one table was not confused for  
    another)
 
G.3 parts of algorithm return what is expected (helps to do refactoring, 
    once we change something in algorithm or data structures or else, 
    some tests break and we have to put in new ones)
 
G.4 functions like to_float() return expected results on actual data

Test suit
=========
 
parse.py tested as following:
  test_parse.py             - this commentary and regresion/bugfixes
  test_parse_classes.py     - some classes on constants (lower-level)
  test_parse_functions.py   - statless functions on constants (lower-level)
  test_parse_pipeline.py    - dataflow from CSV to Dataframes on fixtures (mid-level)
  test_parse_checkpoints.py - selected datapoints on actual data (high-level)
splitters.py   - covered by doctests
cfg.py         - requires some additinal testing/validation, see todo 1 

Coverage
======== 
coverage run --source=. -m pytest
coverage report -m > coverage.output
coverage annotate -d annotate

TODO: exclude test_*.py files from coverage commands
TODO: show coverage as online badge - what is the process to do it?

Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
cfg.py                          134     15    89%   80, 83-84, 100-104, 107, 262-267
files.py                         67     19    72%   50, 77-83, 108-109, 127, 132-136, 140-142
parse.py                        415     42    90%   55-59, 146, 175-176, 179-184, 288-291, 379, 430, 440, 536, 568-571, 599-600, 604, 610, 615, 625-626, 631-632, 639-641, 646-652
splitter.py                      30     10    67%   35, 54, 65, 69-71, 83-84, 116-117
-----------------------------------------------------------

TODO
====
(1) cfg.py: 
    - validate definitions on order of markers  https://github.com/epogrebnyak/mini-kep/issues/22
(2) some useful tests died at https://github.com/epogrebnyak/data-rosstat-kep, need summary of tests for mini-kep
(3) add new defintions to cfg.py and  change dataframe dumps 
(4) todos in coverage (above)
(5) come up with test extension suggestions (put some empty tests / comments in test_*.py files code) 
    - gaps in algorithm behaviour/logic - most important
    - list of funcs and classes (below) 
    - tst_draft.py seceleton initial draft - to be deleted
    - 'annotations' directory         
    - Missing statements (above) - least important  
      
LIST OF  FUNCTIONS AND CLASSES
==============================

test_parse_functions.py:

	def extract_unit(label):
	def extract_varname(label):
	def make_label(vn, unit, sep="_"):
	def split_label(label):

	def get_year(string: str, rx=YEAR_CATCHER):
	def is_year(string: str) -> bool:

	def to_float(text, i=0):

	def month_end_day(year, month):
	def get_date_month_end(year, month):
	def get_date_quarter_end(year, qtr):
	def get_date_year_end(year):
	
	def from_csv(path):
	def read_csv(path):
	def to_csv(rows, path):

test_parse_classes.py:          

	class Row:
	class RowStack:
	class Table:
	class Header:
	class DictMaker:
        
	class Tables:        
    uses:
	    def check_required_labels(tables, pdef):
	    def fix_multitable_units(tables):
	    def get_tables_from_rows_segment(rows_segment, pdef, units=UNITS):
	    def split_to_tables(rows):
      
	class Emitter:
	class Datapoints:
	class Frames:
        
   class Vintage:
   class Collection:        
        
"""

import pytest
import parse
import files

# Regression tests - after bug fixes on occasional errors
def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

if __name__ == "__main__":
    pytest.main(["test_parse.py"])