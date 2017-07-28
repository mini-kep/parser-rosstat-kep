[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 

# mini-kep
Parse MS Word files from Rosstat and save clean macroeconomic time series as CSV at stable URL.

See documentation [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)

# Development notes

- uncomment tests

- sphinx-doc usage:
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
   
- examples:
  - provide CSV source example
  - provide dataframe example
 
- rename to **reader-parser-emitter**:
  - rename kep to csv2df
  - combine rows and splitter modules, make **reader**
  - rename tables to **parser**
  - make **emitter**
  
- testing:
 - check final values in a different procedure 
 
- frontpage
 
- aws:
  - read/copy from bucket as
  - use boto with credentials 
  - save deeper history to bucket
  - gap (2013, x)
