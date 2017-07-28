[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)

# mini-kep
Parse MS Word files from Rosstat and save clean macroeconomic time series as CSV at stable URL.

See documentation [here](http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com)

# Development notes

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
  - uncomment tests
 
- frontpage
 
- aws:
  - read/copy from bucket as
  - use boto with credentials 
  - save deeper history to bucket
  - gap (2013, x)
