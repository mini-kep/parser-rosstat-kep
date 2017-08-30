[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a467743314641b4a22b66b327834367)](https://www.codacy.com/app/epogrebnyak/mini-kep?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=epogrebnyak/mini-kep&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/mini-kep-parcer-for-rosstat-kep-publication/badge/?version=latest)](http://mini-kep-parcer-for-rosstat-kep-publication.readthedocs.io/en/latest/?badge=latest)

           
# Concept

[mini-kep] parses MS Word files from [Rosstat KEP publication][Rosstat], creates pandas dataframes with 
macroeconomic time series and saves them as [CSV files at stable URL][backend]. 

  [mini-kep]: https://github.com/epogrebnyak/mini-kep
  [Rosstat]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
  [backend]: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest

[mini-kep] code has following packages:
   - **locations**: navigate through repo directory structure 
   - **download**: download and unpack rar files from Rosstat website
   - **word2csv**: convert MS Word files to single interim CSV file (Windows-only)
   - **csv2df**: parse interim CSV files and save processed CSV files with annual, quarterly and monthly data


# Latest data

*TODO: add graphs here <https://github.com/epogrebnyak/mini-kep/issues/12>*

*TODO: generate Excel files <https://github.com/epogrebnyak/mini-kep/issues/70>*


# How can I download macroeconomic indicators from here?

You can use macroeconomic indicators in your python code as shown below or 
get latest data as Excel file [kep.xlsx](https://github.com/epogrebnyak/mini-kep/issues/70)

```python

def get_dataframe(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    url = url_base.format(filename)
    return pd.read_csv(url, 
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')

dfa = get_dataframe('a')
dfq = get_dataframe('q')
dfm = get_dataframe('m')
```

More access methods (including saving a local copy) are shown in 
[example_access_data.py](https://github.com/epogrebnyak/mini-kep/blob/dev/src/example_access_data.py).