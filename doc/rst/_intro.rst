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


See more parsing examples `here`_.

