[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/mini-kep-parcer-for-rosstat-kep-publication/badge/?version=latest)](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)
           
Development 
===========

- [mini-kep] inspired by [FRED](https://fred.stlouisfed.org/) and [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science)
- *data-rosstat-kep* is ancestor to *mini-kep*
- project documentation is [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)
- project glossary is [here](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/)

  
Active tasks 
============

These tasks are marked with ['in development' label](https://github.com/epogrebnyak/mini-kep/labels/in%20development)

-----

### review src/kep (doctrints, eye review, refactoring code and tests)

Issue: <https://github.com/epogrebnyak/mini-kep/issues/52>

Guidelines: <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_refactoring.md>

Expected result: 
- [ ] new fixtures

------

### parsing result validation 

Issue: <https://github.com/epogrebnyak/mini-kep/issues/50>

Expected result: 
  - [ ] full coverage of required variables

-------

### resulting df consistency check and transformations

Issue: <https://github.com/epogrebnyak/mini-kep/issues/61>, 
       <https://github.com/epogrebnyak/mini-kep/issues/63>

Work file: <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_df_check.py>

Expected result:
  - [ ] anomalies in ```dfa, dfq, dfm``` revealed
  - [ ] GOV_*_ACCUM differentiated  
    
Prepare tasks
=============

helper module with  dates:
  - [ ] review **filled_dates** mechanism in files.py 

add more parsing definitions:
  - [ ] see [#33 Add more variable definitions ](https://github.com/epogrebnyak/mini-kep/issues/33) 	
  
frontpage:
   - issue <https://github.com/epogrebnyak/mini-kep/issues/18> 
   - workfile <https://github.com/epogrebnyak/mini-kep/tree/master/src/frontend>.
   - [ ] show imported variables or varnames
   - [ ] how many variable were read?
  
testing: 
  - [ ] see <https://github.com/epogrebnyak/mini-kep/issues?q=is%3Aissue+is%3Aopen+label%3Atesting>
  - [ ] test coverage annotate 
  - [ ] check values from sample rows in spec  
  - [ ] uncomment end-to-end test
  - [ ] review previous testing guidelines    
  - [ ] [CSV mock proposal](https://github.com/epogrebnyak/mini-kep/issues/9)
   
  
NOT TODO / LATER
=================

s3 sync:
  - workfile <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_boto_s3_sync.py>
  - issue: <https://github.com/epogrebnyak/mini-kep/issues/51>
  - [ ] local to S3 
  - [ ] S3 to local 
  - [ ] manually save deeper history of s3 files to bucket

-----------

follow-up tasks from spec.py:
   - [ ] use sample in required
   - [ ] short names for variables in FRED style, ```short=```

---------------

sphinx-doc usage:
  - why modules rst?
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
  
----------------  
  
[online coverage badge](https://github.com/epogrebnyak/mini-kep/issues/23)

----------------

document gap (2013, x)

----------------

html docs to bucket:
  - [ ] document why unhappy with readthedocs
  - [x] try restore encoding at readthedocs (maybe python3 issue , will not work)  
  - [ ] uploader to bucket


KINDDA DONE
===========

- [x] [simplify procedure to update new month #29](https://github.com/epogrebnyak/mini-kep/issues/29)

  
DONE
====
- [x] [renaming modules](https://github.com/epogrebnyak/mini-kep/issues/35)
- [x] example.py
- [x] delete from repo: static html
- [x] try ```inv pep8 -f.``` works
- [x] spec.py review
- [x] download an unpack rar files from Rosstat
- [x] helper module with local file paths + maybe also web destination 
