[![Build Status](https://travis-ci.org/mini-kep/parser-rosstat-kep.svg?branch=master)](https://travis-ci.org/mini-kep/parser-rosstat-kep)
[![Coverage badge](https://codecov.io/gh/mini-kep/parser-rosstat-kep/branch/master/graphs/badge.svg)](https://codecov.io/gh/mini-kep/parser-rosstat-kep)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)


Concept
-------

The task is to extract pandas dataframes from MS Word files from [Rosstat KEP publication][Rosstat] and save them as [CSV files][backend]. 

This code replaces a predecessor repo, [data-rosstat-kep](https://github.com/epogrebnyak/data-rosstat-kep), which could not handle vintages of macroeconomic data. 

We require Windows and Word installed to create table dumps from .doc files, but once done parsing CSV files can run on linux machine.   

Interface 
---------
[manage.py](https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/manage.py) does the following job:
- download and unpack MS Word files from Rosstat
- extract tables from Word files and assigns variable names
- create pandas dataframes with time series (at annual, quarterly and monthly frequency) 
- save dataframes as [CSV files at stable URL][backend] 

[kep]: https://github.com/mini-kep/parser-rosstat-kep
[Rosstat]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
[backend]: https://github.com/mini-kep/parser-rosstat-kep/tree/master/data/processed/latest


# Directory structure

[kep] follows [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science) template for 
directory structure. 

[Source code (src) folder](https://github.com/mini-kep/parser-rosstat-kep/tree/master/src):
   - **download**: download and unpack rar files from Rosstat website
   - **word2csv**: convert MS Word files to single interim CSV file (Windows-only)
   - **csv2df**: parse interim CSV files and save processed CSV files with annual, quarterly and monthly data
   - **finaliser.py** 

[Processed data folder](https://github.com/mini-kep/parser-rosstat-kep/tree/master/data/processed)
has datasets by year and month (vintages).


# Access to parsing result

[getter.py](https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/getter.py) 
is an entry point to get parsed data.

```python
import pandas as pd

def get_dataframe_from_web(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    url = url_base.format(filename)
    return pd.read_csv(url, converters={0: pd.to_datetime}, index_col=0)

dfa = get_dataframe_from_web('a')
dfq = get_dataframe_from_web('q')
dfm = get_dataframe_from_web('m')
```

# Data in Excel

 Here is the latest data in Excel (but use of csv is still encouraged): 
 
 - [kep.xlsx](https://github.com/epogrebnyak/mini-kep/blob/master/output/kep.xlsx?raw=true)
  
# Repo management

Around [this schedule](http://www.gks.ru/gis/images/graf-oper2017.htm) on a Windows machine I run:   

```
invoke add <year> <month>
```

and commit to this repo.

This command:
- downloads a rar file from Rosstat, 
- unpacks MS Word files, 
- dumps all tables from MS Word files to an interim CSV file, 
- parses interim CSV file to three dataframes by frequency 
- validates parsing result
- transforms some variables (eg. deaccumulates government expenditures)
- saves dataframes as processed CSV files
- saves csv for latest date
- saves an Excel file for latest date.

Same job is done by [manage.py](https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/manage.py)

# Parcer summary

Parcer              |  mini-kep 
--------------------|----------------------------------------
Job                 |  Parse sections of Short-term Economic Indicators (KEP) monthly Rosstat publication 
Source URL          |  [Rosstat KEP page](http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391)
Source type         |  MS Word  <!-- Word, Excel, CSV, HTML, XML, API, other -->
Frequency           |  Monthly
When released       |  Start of month as in [schedule](http://www.gks.ru/gis/images/graf-oper2017.htm) 
Code                | <https://github.com/epogrebnyak/mini-kep/tree/master/src/>
Test health         | [![Build Status](https://travis-ci.org/mini-kep/parser-rosstat-kep.svg?branch=master)](https://travis-ci.org/mini-kep/parser-rosstat-kep)
Test coverage       |  [![Coverage badge](https://codecov.io/gh/mini-kep/parser-rosstat-kep/branch/master/graphs/badge.svg)](https://codecov.io/gh/mini-kep/parser-rosstat-kep)
Documentation       |  [![Documentation Status](https://readthedocs.org/projects/mini-kep-parcer-for-rosstat-kep-publication/badge/?version=latest)](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)
CSV endpoint        | <https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest>
Transformation      |  Government revenue/expenses deaccumaulated to monthly values 
Validation          |  Hardcoded checkpoints and consistency checks 


All historic raw data available on internet? 
- [ ] Yes
- [x] No (data prior to 2016-12 is in this repo only)  

Is scrapper automated (can download required information from internet  without manual operations)? 
- [x] Yes
- [ ] No 
