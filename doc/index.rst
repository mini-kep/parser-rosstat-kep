.. kep documentation master file, created by
   sphinx-quickstart on Sun Jul 23 02:39:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mini-kep documentation
==================================

`mini-kep <https://github.com/epogrebnyak/mini-kep>`_ aims to parse `archived MS Word files from Rosstat`_ 
to obtain clean pandas dataframes with macroeconomic time series and save them as `processed CSV files at stable URL <_latest>`_ for further use. 

.. _archived MS Word files from Rosstat:  http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391

.. _latest: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest

Steps involved in the parsing pipeline are the following:

- **manually** (*FIXME*):

  - download zip/rar file for a specified month
  - unpack this zip/rar file to a local folder

- **word2csv**: convert several MS Word files to single interim CSV file (see `example <https://github.com/epogrebnyak/mini-kep/blob/master/data/interim/2017/05/tab.csv>`_)

- **csv2df**: parse interim CSV file to obtain `processed CSV files <https://github.com/epogrebnyak/mini-kep/blob/master/data/interim/2017/05/tab.csv>`_ with annual, quarterly and monthly data.

Also in this module:

- **access_data**: sample code to download data from stable URL and save its local copy   
- **frontpage**: try making README.md_ a nice page with graphs

.. _README.md: https://github.com/epogrebnyak/mini-kep/blob/master/README.md


TODO
----
- provide CSV source example
- provide dataframe example
- more examples to examples.rst text


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   kep
   kep.files
   kep.rows
   kep.spec
   kep.splitter
   kep.tables
   kep.vintage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
