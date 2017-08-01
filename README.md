[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)

# mini-kep
Parse MS Word files from Rosstat and save clean macroeconomic time series as CSV at stable URL.

See documentation [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)


#  Directions for work   

## D1. Review modules in src/kep:

Intent: document and test current stable version (found in *master* branch)

Review modules:
- [x] kep.files 
- [ ] kep.spec 
- [ ] kep.rows
- [ ] kep.splitter
- [ ] kep.tables
- [ ] kep.vintage

By module do:
 - (optional) propose/discuss/commit/eye review changes to code  
 - write assert statements and edit/enhance tests
 - edit module docstrings:
   - module
   - classes, public methods and functions used in other parts of the program
   - other docstrings/comments where needed
 - code examples for documentation where needed  
 - make list of refactoring / enhancements by writing TODO and FIXME in code 
 
For docstrings we use <https://google.github.io/styleguide/pyguide.html#Comments>. 

For testing we use py.test and make follwoing kinds of tests depending on situation:
 - unit tests:
   - make sure a method is callable (like for ```__repr__()```), no control values 
   - unit test with simple control values for a small fucntion / method, ususally public ones 
 - behaviour tests with fixtures / mocks for larger functionalities
 - end-to-end test on sample or real data  

Current issue:

- [#38 document and refactor kep.spec](https://github.com/epogrebnyak/mini-kep/issues/38)

Finished work example: **kep.files**:
- code: <https://github.com/epogrebnyak/mini-kep/blob/master/src/kep/files.py>
- test: https://github.com/epogrebnyak/mini-kep/blob/master/src/kep/tests/test_files.py
- rst: <https://github.com/epogrebnyak/mini-kep/blob/master/doc/kep.files.rst>
- documentation: <http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com/kep.files.html>


## D2. List refactroing proposals as issues

 
## D3. Extend parsing definitions

See [reference]<https://github.com/epogrebnyak/mini-kep/tree/master/reference/parsing_definitions>

## D4. Frontend for parsing result

See <> and individual tasks below

## D5. Extend functionality 

- [ ] manage download file and unpack
- [ ] managing resources on aws s3

# Task list

## Cricital path tasks 

- extend variable definition (= **D3**)

- variable transformation layer:
  - GOV_ACCUM

- examples:
  - provide CSV source example
  - provide dataframe example
 
- testing:
  - check final values in a different procedure using sample 
  - uncomment end-to-end tests
 
- frontpage (=**D4**):
  - show imported variables or varnames in README.md

## Enhancements

- aws (part of **D5**):
  - use boto with credentials 
  - read/copy data from bucket  
  - save deeper history to bucket
  - document gap (2013, x)
  
## Lower priority

- rename modules to **reader-parser-emitter**:
  - rename kep to csv2df
  - combine rows and splitter modules, make **reader**
  - rename tables to **parser**
  - make **emitter**

- housekeeping:
  - try ```inv pep8 -f.```

- sphinx-doc usage:
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
  
## **WONTFIX**
- [online coverage badge](https://github.com/epogrebnyak/mini-kep/issues/23)

## Done
- [x] delete from repo: static html
