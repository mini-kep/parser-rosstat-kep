.. kep documentation master file, created by
   sphinx-quickstart on Sun Jul 23 02:39:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mini-kep documentation
==================================

`mini-kep`_  parses MS Word files from `Rosstat 'KEP' publication`_. It results in pandas
dataframes with macroeconomic time series and saves clean `processed CSV files at stable URL`_.

Inspired / affected by:

- `FRED`_, where economic data is handled so well
- `cookiecutter-data-science`_, where `analysis is a DAG`_
- intense attraction to reproducible analysis and clean code  

.. _FRED: https://fred.stlouisfed.org/
.. _cookiecutter-data-science: https://github.com/drivendata/cookiecutter-data-science
.. _analysis is a DAG: http://drivendata.github.io/cookiecutter-data-science/#analysis-is-a-dag


Parser pipeline
~~~~~~~~~~~~~~~

Steps involved in parsing pipeline are the following:

-  **manually** (*FIXME*):

   -  download zip/rar file for a specified month `from Rosstat website`_
   -  unpack MS Word files to a local folder

-  **word2csv**: convert MS Word files to single interim CSV file (see
   `example`_)

-  **csv2df**: parse interim CSV file to obtain `processed CSV files`_
   with annual, quarterly and monthly data.

Also in `/src`_ folder:

-  **access\_data**: sample code to download data from stable URL and
   save a local copy
-  **frontpage**: add tables and graphs to `README.md`_

.. _mini-kep: https://github.com/epogrebnyak/mini-kep
.. _Rosstat:  http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
.. _Rosstat 'KEP' publication: Rosstat_
.. _latest: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest
.. _processed CSV files at stable URL: latest_
.. _from Rosstat website: Rosstat_
.. _example: https://github.com/epogrebnyak/mini-kep/blob/master/data/interim/2017/05/tab.csv
.. _processed CSV files: latest_
.. _/src: https://github.com/epogrebnyak/mini-kep/tree/master/src
.. _README.md: https://github.com/epogrebnyak/mini-kep/blob/master/README.md

**csv2df** modules
-------------------

.. toctree::
   :maxdepth: 2
   
   kep.files
   kep.spec
   kep.rows   
   kep.splitter
   kep.tables
   kep.vintage

TODO
----
- sphinx-doc usage:

   - include intro.md to index.rst
   - warnings in compile (copying static files...  
     WARNING: html_static_path entry '...mini-kep-master\\doc\\_static' does not exist)

- examples:

  - provide CSV source example
  - provide dataframe example

- commenting:

  - add docstrings + may extract docstrings as list?
  - what docstrign style for module level?
  
- coding:  

  - change naming to **reader-parser-emitter**
  - combine rows and splitter modules, make **reader**
  - rename tables to **parser**
  - make **emitter**?
  - rename kep to csv2df
  - (make folders a package)
  
- testing:

  - check final values in a different fashion
  - restore travis badge


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`