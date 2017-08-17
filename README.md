[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/mini-kep-parcer-for-rosstat-kep-publication/badge/?version=latest)](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)
           

# Concept

[mini-kep] parses MS Word files from [Rosstat KEP publication][Rosstat], creates pandas dataframes with 
macroeconomic time series and saves them as [CSV files at stable URL][backend]. 

  [mini-kep]: https://github.com/epogrebnyak/mini-kep
  [Rosstat]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
  [backend]: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest

# Latest data

*TODO: add graphs here <https://github.com/epogrebnyak/mini-kep/issues/12>*

*TODO: generate Excel files <https://github.com/epogrebnyak/mini-kep/issues/70>*


# How I download macroeconomic indicators from here?

### Excel file

Latest data is in [kep.xlsx](https://github.com/epogrebnyak/mini-kep/issues/70).


### Work with CSV 

You can use macroeconomic indicators in your python code as:

```python
import pandas as pd

# monthly data in *dfm* dataframe
url_m = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/dfm.csv"
dfm = pd.read_csv(url_m)

# quarterly data in *dfq* dataframe
url_q = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/dfq.csv"
dfq = pd.read_csv(url_q)

# annual data in *dfa* dataframe
url_a = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/dfa.csv"
dfa = pd.read_csv(url_a)
```

or, with a nicer date index formatting as:

```python

def get_dataframe(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    url = url_base.format(filename)
    return pd.read_csv(url, 
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')

dfa = get_dataframe('a')
dfq = get_dataframe('q')
dfm = get_dataframe('m')
```

Check other access methods [here](https://github.com/epogrebnyak/mini-kep/blob/dev/src/access_data/).

# Development 

- [mini-kep] inspired by [FRED](https://fred.stlouisfed.org/) and [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science)
- *data-rosstat-kep* is ancestor to *mini-kep*
- project documentation is [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com). FIXME: readthedocs not updated.
- [project glossary](https://github.com/epogrebnyak/mini-kep/blob/master/doc/glossary.rst).

### Workflow


|    Rosstat             |      mini-kep                 |     Stable URL
|------------------------|-------------------------------|-------------------
|   Releases Word files  |                               |
|                        |  Download and unpack          |       
|                        |  Convert MS Word files        |   
|                        |  Parse, validate and publish  |       
|                        |                               |  Read clean CSV files  			

- **Rosstat** issues KEP publication every month as rar'ed Word files
- **mini-kep**: 
   - downloads and unpacks rar files from website, or S3 bucket (prior to 2017) *(not implemented, TODO)*
   - dumps MS Word files to interim CSV files
   - parses interim CSV files and verifies data
   - saves output as three CSV files (annual, quarterly and monthly)
- **End user**:
   - imports machine-readable CSV files from [stable URL](https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest) using pandas or R.

### Mini-kep subpackages

-   **word2csv**: convert MS Word files to single interim CSV file
-   **csv2df**: parse interim CSV file to obtain processed CSV files with annual, quarterly and monthly data.

Also in [/src](https://github.com/epogrebnyak/mini-kep/tree/master/src) folder:

-   **access\_data**: sample code to download data from stable URL and save a local copy
-   **frontpage**: add tables and graphs to [README.md](https://github.com/epogrebnyak/mini-kep/blob/master/VALUES.md)


### Parcer work example

**csv2df** parcer is at core of **mini-kep**. Its work is illustarted by [example here](https://github.com/epogrebnyak/mini-kep/blob/dev/src/example.py).

**csv2df** translates text like this:

```
Объем ВВП, млрд.рублей / Gross domestic product, bln rubles					
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044
```

to pandas dataframes:

```
            year  GDP_bln_rub
1999-12-31  1999       4823.0
2000-12-31  2000       7306.0
```

```
            year  qtr  GDP_bln_rub
1999-03-31  1999    1        901.0
1999-06-30  1999    2       1102.0
1999-09-30  1999    3       1373.0
1999-12-31  1999    4       1447.0
2000-03-31  2000    1       1527.0
2000-06-30  2000    2       1697.0
2000-09-30  2000    3       2038.0
2000-12-31  2000    4       2044.0
```

  
Active tasks 
============

These tasks are marked with ['in development' label][in_dev]

[in_dev]: https://github.com/epogrebnyak/mini-kep/labels/in%20development


### review src/kep (doctrints, eye review, refactoring code and tests)

Issue: <https://github.com/epogrebnyak/mini-kep/issues/52>

Guidelines: <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_refactoring.md>

Refactoring, documentation, testing for:
- [x] kep.files 
- [x] kep.spec 
- [ ] kep.rows (in progress)
- [x] kep.splitter
- [ ] kep.tables
- [ ] kep.vintage
- [ ] kep.validator, also as [Issue #50](https://github.com/epogrebnyak/mini-kep/issues/50)

### parsing result validation 

Issue: <https://github.com/epogrebnyak/mini-kep/issues/50>

Expected result: 
  - [ ] new file src/test/test_validator.py

### download an unpack rar files from Rosstat

Issue: <https://github.com/epogrebnyak/mini-kep/issues/30>

Work file: <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_download.py>

Expected result: 
  - [x] download rar file from Rosstat
  - [x] unrar MS Word files
  - [ ] wrap unrar for linux usage
  - [ ] save Word files to designated folder
  - [ ] rely on new date helper to check what can be downloaded

### resulting df consistency check and transformations

Issue: <https://github.com/epogrebnyak/mini-kep/issues/61>, 
       <https://github.com/epogrebnyak/mini-kep/issues/63>

Work file: <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_df_check.py>

Expected result:
  - [ ] anomalies in ```dfa, dfq, dfm``` revealed
  - [ ] GOV_*_ACCUM differentiated  
    
 
Prepare tasks
=============

Tasks below require more specification. 


[simplify procedure to update new month #29](https://github.com/epogrebnyak/mini-kep/issues/29)

helper module with  dates:
  - [ ] review **filled_dates** mechanism in files.py 

helper module with local file paths:  
  - [ ] maybe also web destination 
  
html docs to bucket:
  - [ ] document why unhappy with readthedocs
  - [ ] try restore encoding at readthedocs (maybe python3 issue , will not work)  
  - [ ] uploader to bucket
  
s3 sync:
  - workfile <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_boto_s3_sync.py>
  - issue: <https://github.com/epogrebnyak/mini-kep/issues/51>
  - [ ] local to S3 
  - [ ] S3 to local 
  - [ ] manually save deeper history of s3 files to bucket

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

[renaming modules](https://github.com/epogrebnyak/mini-kep/issues/35)
   - [ ] rename kep to csv2df
   - [ ] csv2df.reader, parser, emitter

follow-up tasks from spec.py:
   - [ ] use sample in required
   - [ ] short names for variables in FRED style, ```short=```

- sphinx-doc usage:
  - why modules rst?
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
  
- [online coverage badge](https://github.com/epogrebnyak/mini-kep/issues/23)

- document gap (2013, x)
  
DONE
====
- [x] example.py
- [x] delete from repo: static html
- [x] try ```inv pep8 -f.``` works
- [x] spec.py review
