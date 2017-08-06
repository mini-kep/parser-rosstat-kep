[![Gitter chat](https://badges.gitter.im/mini-kep/gitter.png)](https://gitter.im/mini-kep)
[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)

# mini-kep
Parse MS Word files from Rosstat and save clean macroeconomic time series as CSV at stable URL.

See documentation [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)


# TODO 1: refactoring-documentation-examples-testing 

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
