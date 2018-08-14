Objective
=========

Extract data from CSV file using parsing instructions and units of measurement definition. 
Run over monthly data releases to learn about economic indicator revisions.

Inputs
======

- one CSV file (as `sandbox.CSV_TEXT`)
- parsing instructions (as `sandbox.INTRUCTIONS_DOC`)
- default units of measurement (as `sandbox.UNITS_DOC`)

Comment: units of measurement can be a part of parsing instructions, 
         but they are reused often, that is why they are a separate 
         input parameter. 

Output
======

Three pandas dataframes at annual, quarterly and monthly frequencies 
(`dfa`, `dfq`, `dfm`)

    
Pseudocode
==========

1. split incoming CSV file to tables, with headers and data
2. read parsing instructions, they are either common instructions for all of the document or instuctions for document segments
2.1 for common instructions: 
    - apply parsing instructions to table headers in block of tables 
      to obtain variable labels (variable name and unit of measurement) 
    - check all expected variable labels are found in tables 
	- save parsed tables to queue of parsed tables
2.2. segment instructions
   -  limit block of tables 
   -  apply parsing instructions for this segment as in 2.1 
3. emit datapoints from queue of parsed tables
4. check datapoints with control values
5. create pandas dataframes by frequency, transform (deacculmulate) some dataframes

NOTES
=====
- [Profiling reference](https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code)
- [Packaging reference](http://python-packaging.readthedocs.io/en/latest/testing.html)
- [Module and subpackaige naming](https://gitlab.com/warsaw/mailman/tree/master/src/mailman) 


TODOS
=====
- [ ] restore more definitons
- [ ] tests for load subpackage omitted
- [ ] coverage of checkpoints

ERRORS
======
- [ ] must use 'a' as 'm12' in 'fiscal' row format


IDEAS
=====
- [ ] plot(label, freq)
- [ ] varibale descriptions (ru and en)
- [ ] grouping of variables for Excel file 
- [ ] add check all variables in parsing definition are covered with checkpoints 
- [ ] read environment variable /  structure as package with setuptools
- [ ] move locations.py inside kep.package

WONTFIX
=======
- /index.html#module-kep
- [ ] better check than `assert not dfa.empty`
- [ ] need better regex in kep.filters

FINAL USE
=========
- plot deviations between first and last estimate
  - make a special dataframe format
- extend parsing definitions for more variables
- upload to database
- plot everything for one month
- save xls
- write variable names

DONE
====
- [x] https://github.com/mini-kep/parser-rosstat-kep/blob/archive_master_1/src/kep/parsing_definition/default.json
- [x] write parsign result in session - 110 months, 5 labels
- [x] fixed: fails with corporate profits
- [x] restore to_latest() and to_excel() functions
- [x] get latest months in 2018 
- [x] restore download/unpack/convert functionality outside parser
- run Session on several CSV files
  - [x] two files in data
  - [x] actual files since 2007
- [x] estimate running time 
- [x] more clear yaml import
- [x] kep.filters has duplicate functions
- [x] speedups
- [x] find old definition in git eg 
- [x] tests for dataframes onitted

Writeup
=======

