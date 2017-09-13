[![Build Status](https://travis-ci.org/mini-kep/parser-rosstat-kep.svg?branch=master)](https://travis-ci.org/mini-kep/parser-rosstat-kep)

**TODO: review badges after migration**

[![Coverage badge](https://codecov.io/gh/epogrebnyak/mini-kep/branch/master/graphs/badge.svg)](https://codecov.io/gh/epogrebnyak/mini-kep)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/mini-kep-parcer-for-rosstat-kep-publication/badge/?version=latest)](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)

           
# Concept
[parser-rosstat-kep][kep] downloads MS Word files from [Rosstat KEP publication][Rosstat], 
assigns variable names to tables found and creates pandas dataframes with 
macroeconomic time series and saves them as [CSV files at stable URL][backend]. 

  [kep]: https://github.com/mini-kep/parser-rosstat-kep
  [Rosstat]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
  [backend]: https://github.com/mini-kep/parser-rosstat-kep/tree/master/data/processed/latest

[kep] follows [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science) template for 
directory structure. 

The parcer itself consists of following subpackages:
   - **download**: download and unpack rar files from Rosstat website
   - **word2csv**: convert MS Word files to single interim CSV file (Windows-only)
   - **csv2df**: parse interim CSV files and save processed CSV files with annual, quarterly and monthly data

[getter.py](https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/getter.py) is 
an entry point to get parsed data.
   
[kep] is inspired by [FRED](https://fred.stlouisfed.org/) and replaces a predecessor repo,
[data-rosstat-kep](https://github.com/epogrebnyak/data-rosstat-kep), which could not handle vintages of
macroeconomic data well. 

Project documentation is [here](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)
and little glossary [here](https://github.com/epogrebnyak/mini-kep/blob/master/doc/rst/glossary.rst).
   

# Latest data

*TODO: add spline graphs here <https://github.com/epogrebnyak/mini-kep/issues/12>*


# How do I download macroeconomic indicators from here?

```python

def get_dataframe_from_web(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    url = url_base.format(filename)
    return pd.read_csv(url, 
                       converters={0: pd.to_datetime},
                       index_col='0)

dfa = get_dataframe_from_web('a')
dfq = get_dataframe_from_web('q')
dfm = get_dataframe_from_web('m')
```

Check more access methods at
[getter.py](https://github.com/epogrebnyak/mini-kep/blob/dev/src/getter.py).


# Can I get this data in Excel?

 Here is the latest data in Excel: 
 
 - [kep.xlsx](https://github.com/epogrebnyak/mini-kep/blob/master/output/kep.xlsx?raw=true)
  
# How do you update this repo?

Around [this schedule](http://www.gks.ru/gis/images/graf-oper2017.htm) on a Windows machine I run:   

```
invoke add <year> <month>
```

and commit to this repo.

Basically this command:
- downloads a rar file from Rosstat, 
- unpacks MS Word files, 
- dumps all tables to an interim CSV file, 
- parses interim CSV file to dataframes by frequency 
- validates parsing result
- transforms some variables
- saves dataframes as processed CSV files
- saves an Excel file for latest date.


See [DEV.md](https://github.com/epogrebnyak/mini-kep/blob/master/DEV.md) for development notes/roadmap. 


# Parcer summary

Parcer              |  mini-kep 
--------------------|----------------------------------------
Job                 |  Parse sections of Short-term Economic Indicators (KEP) monthly Rosstat publication 
Source URL          |  [Rosstat KEP page](http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391)
Source type         |  MS Word  <!-- Word, Excel, CSV, HTML, XML, API, other -->
Frequency           |  Monthly
When released       |  Start of month as in [schedule](http://www.gks.ru/gis/images/graf-oper2017.htm) 
Code                | <https://github.com/epogrebnyak/mini-kep/tree/master/src/>
Controller          |  TODO: Add here
Test health         | [![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep)
Test coverage       |  [![Coverage badge](https://codecov.io/gh/epogrebnyak/mini-kep/branch/master/graphs/badge.svg)](https://codecov.io/gh/epogrebnyak/mini-kep)
Documentation       |  [![Documentation Status](https://readthedocs.org/projects/mini-kep-parcer-for-rosstat-kep-publication/badge/?version=latest)](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)
CSV endpoint        | <https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest>
List of variables   |  TODO: Add here
Transformation      |  Government revenue/expenses deaccumaulated to monthly values 
Validation          |  Hardcoded checkpoints and consistency checks 


All historic raw data available on internet? 
- [ ] Yes
- [x] No (data prior to 2016-12 is in this repo only)  

Is scrapper automated (can download required information from internet  without manual operations)? 
- [x] Yes
- [ ] No 
