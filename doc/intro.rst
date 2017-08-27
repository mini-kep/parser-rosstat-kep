Concept
=======

**mini-kep** parses MS Word files from Rosstat KEP publication, 
creates pandas dataframes with macroeconomic time series and saves 
them as CSV files at stable URL. 

Workflow
========

+-------------------------+-----------------------------------------+------------------------------+
| Rosstat                 | mini-kep                                | Stable URL                   |
+=========================+=========================================+==============================+
| Publishes Word files…   |                                         |                              |
+-------------------------+-----------------------------------------+------------------------------+
|                         | downloads, parses and publishes         |                              |
+-------------------------+-----------------------------------------+------------------------------+
|                         |                                         | User reads clean CSV files   |
+-------------------------+-----------------------------------------+------------------------------+

- **Rosstat** issues KEP publication every month as RAR-archived Word files.
- **mini-kep** does the following:
        -  **download**: download and unpack rar files from Rosstat website
	
	     - *TODO: download from S3 bucket prior to 2016-12* 
	
	-  **word2csv**: convert MS Word files to single interim CSV file
	-  **csv2df**: parse interim CSV file and save processed CSV files with
	   annual, quarterly and monthly data
	-  **frontpage**: make tables and graphs to `README.md`_
- Machine-readable CSV files are available at
   https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest. 
- **End user** can import macroeconomic indicators to your R/pandas code from
  these files (see `access example`_)  

.. _access example: https://github.com/epogrebnyak/mini-kep/blob/master/src/example_access_data.py
.. _README.md: https://github.com/epogrebnyak/mini-kep/blob/master/VALUES.md 

Example
=======

On input we have text like this (from MS Word files):

::

    Объем ВВП, млрд.рублей / Gross domestic product, bln rubles                 
    1999    4823    901 1102    1373    1447
    2000    7306    1527    1697    2038    2044

it translates into pandas dataframes:

::

    dfa
    Out: 
                year  GDP_bln_rub
    1999-12-31  1999       4823.0
    2000-12-31  2000       7306.0
	
    dfq
    Out: 
                year  qtr  GDP_bln_rub
    1999-03-31  1999    1        901.0
    1999-06-30  1999    2       1102.0
    1999-09-30  1999    3       1373.0
    1999-12-31  1999    4       1447.0
    2000-03-31  2000    1       1527.0
    2000-06-30  2000    2       1697.0
    2000-09-30  2000    3       2038.0
    2000-12-31  2000    4       2044.0

See more parsing examples `here`_.

