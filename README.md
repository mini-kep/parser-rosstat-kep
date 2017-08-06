[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)

# mini-kep

[mini-kep] parses MS Word files from [Rosstat KEP publication], creates pandas dataframes with 
macroeconomic time series and saves them as [CSV files at stable URL]. Inspired by [FRED] and 
[cookiecutter-data-science]. 

Check documentation [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)
and examples [here](https://github.com/epogrebnyak/mini-kep/blob/dev/src/example1.py)

```
(1) Rosstat -> (2) mini-kep -> (3) CSV files at https://goo.gl/Cr5mSZ -> (4) your code with R/pandas
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

# TODO 1: refactoring-documentation-examples-testing 

Review modules:
- [x] kep.files 
- [x] kep.spec 
- [ ] kep.rows
- [x] kep.splitter
- [ ] kep.tables
- [ ] kep.vintage

## Refactoring 

See <todo_refactoring.md>:

## Examples
  - provide CSV source example
  - provide dataframe example

## Testing 
- test coverage annotate 
- check values from sample rows in spec  
- uncomment end-to-end tests
- see previous testing guidelines  

# TODO 2: frontpage

## Frontpage:

Show imported variables or varnames in README.md

See <https://github.com/epogrebnyak/mini-kep/tree/master/src/frontend>

## Parsing result statistics

How many variable were read?

# TODO 3: parsing parameters 

## More definitions 

Extend variable definitions
See also <https://github.com/epogrebnyak/mini-kep/tree/master/reference/parsing_definitions>

# TODO 4: other

## Transformations

Variable transformation layer:
  - need to diff the GOV_ACCUM
  
## Download and s3

- Download file and unpack

- Sync with aws s3 - <dev_todo/task_boto_download.py>:
  - [ ] local to S3 
  - [ ] S3 to local 

- Manually save more files to s3
  - save deeper history to bucket
  
- **filled_dates** mechanism   

- write documentation to AWS

 
# WONTFIX
 
- <not_todo_rename_everything.md>

- sphinx-doc usage:
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
  
- [online coverage badge](https://github.com/epogrebnyak/mini-kep/issues/23)

- document gap (2013, x)
  
  
## DONE
- [x] delete from repo: static html
- [x] try ```inv pep8 -f.``` works
