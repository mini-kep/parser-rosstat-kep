[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)

# mini-kep

[mini-kep] parses MS Word files from [Rosstat KEP publication], creates pandas dataframes with 
macroeconomic time series and saves them as [CSV files at stable URL]. Inspired by [FRED] and 
[cookiecutter-data-science]. 

Check documentation [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)
and examples [here](https://github.com/epogrebnyak/mini-kep/blob/dev/src/example1.py)

```
(1) Rosstat -> (2) mini-kep -> (3) clean CSV files -> (4) your code with R/pandas
```
1. Rosstat publishes KEP publication every month as archive of Word files
2. mini-kep parses Word files and saves output as three CSV files (annual, quarterly and monthly)
3. CSV files are available at <https://goo.gl/Cr5mSZ> 
4. you can import Russian macroeconomic indicators to your R/pandas code from these files  


Parser pipeline
===============

-   **manually** (*FIXME*):
    -   download zip/rar file for a specified month [from Rosstat website]
    -   unpack MS Word files to a local folder
-   **word2csv**: convert MS Word files to single interim CSV file (see [example])
-   **csv2df**: parse interim CSV file to obtain [processed CSV files][processed CSV files at stable URL] with annual, quarterly and monthly data.

Also in [/src] folder:

-   **access\_data**: sample code to download data from stable URL and save a local copy
-   **frontpage**: add tables and graphs to [README.md]

  [mini-kep]: https://github.com/epogrebnyak/mini-kep
  [Rosstat ‘KEP’ publication]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
  [processed CSV files at stable URL]: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest
  [FRED]: https://fred.stlouisfed.org/
  [cookiecutter-data-science]: https://github.com/drivendata/cookiecutter-data-science
  [example]: https://github.com/epogrebnyak/mini-kep/blob/master/data/interim/2017/05/tab.csv
  [/src]: https://github.com/epogrebnyak/mini-kep/tree/master/src
  [README.md]: https://github.com/epogrebnyak/mini-kep/blob/master/VALUES.md

# TODO 

## TODO: [# 52 review rows, tables, vintage](https://github.com/epogrebnyak/mini-kep/issues/52)

refactoring-documentation-testing at **kep**:
- [x] kep.files 
- [x] kep.spec 
- [ ] kep.rows
- [x] kep.splitter
- [ ] kep.tables
- [ ] kep.vintage


## TODO: edit example1.py

 - [provide CSV source example](https://github.com/epogrebnyak/mini-kep/issues/9)
 - [comaprison of values in dataframe](https://github.com/epogrebnyak/mini-kep/issues/50)

# TODO: Download and s3 sync

- [ ] [Download files](https://github.com/epogrebnyak/mini-kep/issues/30)

- [ ] Unpack zip/rar files 

- [#51: Sync with aws s3](https://github.com/epogrebnyak/mini-kep/issues/51)
  at [task_boto_download.py](https://github.com/epogrebnyak/mini-kep/blob/dev/todo_task_boto_s3_sync.py):
  - [ ] local to S3 
  - [ ] S3 to local 
  - [ ] html docs to bucket 
  - [ ] must manually save deeper history of s3 files to bucket

  
# Prepare issues

See [tag](https://github.com/epogrebnyak/mini-kep/issues?q=is%3Aissue+is%3Aopen+label%3A%22edit+task+specification%22)


1. add more parsing definitions:
  - see [#33 Add more variable definitions ](https://github.com/epogrebnyak/mini-kep/issues/33) 	
  
1. frontpage:
   - Issue [#18](https://github.com/epogrebnyak/mini-kep/issues/18). See also <https://github.com/epogrebnyak/mini-kep/tree/master/src/frontend>.
   - show imported variables or varnames
   - How many variable were read?

1. transformations:
  - [ ] Variable transformation layer - need to diff the GOV_ACCUM  
   
1. testing: 
  - see <https://github.com/epogrebnyak/mini-kep/issues?q=is%3Aissue+is%3Aopen+label%3Atesting>
  - [ ] test coverage annotate 
  - [ ] check values from sample rows in spec  
  - [ ] uncomment end-to-end tests
  - [ ] review previous testing guidelines    
   
1. [Simplify procedure to update new month #29](https://github.com/epogrebnyak/mini-kep/issues/29):
  -  may also review **filled_dates** mechanism in files.py 
 
1. follow-up tasks from spec.py:
   - ```# TODO: use sample in required```
   - ```# TODO: short names for variables in FRED style, short=```
 
1. [#35 naming modules](https://github.com/epogrebnyak/mini-kep/issues/35)
  
# NOT TODO

- sphinx-doc usage:
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
  
- [online coverage badge](https://github.com/epogrebnyak/mini-kep/issues/23)

- document gap (2013, x)
  
## DONE
- [x] delete from repo: static html
- [x] try ```inv pep8 -f.``` works
- [x] spec.py review