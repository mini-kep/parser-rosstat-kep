.. kep documentation master file, created by
   sphinx-quickstart on Sun Jul 23 02:39:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mini-kep documentation
==================================

`mini-kep`_ parses MS Word files from `Rosstat KEP publication`_, 
creates pandas dataframes with macroeconomic time series and saves 
them as `CSV files at stable URL <https://goo.gl/Cr5mSZ>`_. 
Inspired by `FRED`_ and `cookiecutter-data-science`_.

.. _mini-kep: https://github.com/epogrebnyak/mini-kep
.. _Rosstat KEP publication: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
.. _processed CSV files: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest
.. _FRED: https://fred.stlouisfed.org/
.. _cookiecutter-data-science: https://github.com/drivendata/cookiecutter-data-science

Check documentation `here`_  and examples `here <https://github.com/epogrebnyak/mini-kep/blob/dev/src/example1.py>`__.

.. _here: http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com


How it works
============

::

    (1) Rosstat -> (2) mini-kep -> (3) clean CSV files -> (4) your code in R/pandas

#. Rosstat publishes KEP publication every month as archive of Word
   files
#. mini-kep parses Word files and saves output as three CSV files
   (annual, quarterly and monthly)
#. CSV files are available at https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest,
   or https://goo.gl/Cr5mSZ
#. you can import Russian macroeconomic indicators to your R/pandas code
   from these files

Parser pipeline
===============
**mini-kep** work involves following stages:

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

.. _from Rosstat website: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
.. _example: https://github.com/epogrebnyak/mini-kep/blob/master/data/interim/2017/05/tab.csv
.. _/src: https://github.com/epogrebnyak/mini-kep/tree/master/src
.. _README.md: https://github.com/epogrebnyak/mini-kep/blob/master/VALUES.md

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`