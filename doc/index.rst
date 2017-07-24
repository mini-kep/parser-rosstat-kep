.. kep documentation master file, created by
   sphinx-quickstart on Sun Jul 23 02:39:55 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mini-kep documentation
==================================

``mini-kep`` aims to parse archived MS Word files from Rosstat to obtain clean pandas dataframes and CSV files 
with macroeconomic time series.

Data source can be found at `Rosstat website`_
.. Rosstat website: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391

Steps involved in the parsing pipeline are the following:

- download zip/rar file with monthly publication (*manually*)
- unpack archive to local folder (*manually*)
- **word2csv**: convert several MS Word files to single interim CSV file
- **csv2df**: parse interim CSV file to obtain processed CSV files holding data at annual, quarterly and monthly frequencies.  

Most of work documented here relates to **csv2df**.  

Also in this module:

- **access_data**: sample code to download data from stable URL and save its local copy   
- **frontpage**: try making README.md_ a nice page with graphs

.. README.md: https://github.com/epogrebnyak/mini-kep/blob/master/README.md


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
