[mini-kep] parses MS Word files from [Rosstat KEP publication][Rosstat], creates pandas dataframes with 
macroeconomic time series and saves them as [CSV files at stable URL][backend]. 

  [mini-kep]: https://github.com/epogrebnyak/mini-kep
  [Rosstat]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
  [backend]: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest

[mini-kep] follows [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science) template for 
directory structure. 

The parcer itself consists of following packages (in 
[src](https://github.com/epogrebnyak/mini-kep/blob/master/src/) folder):
   - **download**: download and unpack rar files from Rosstat website
   - **word2csv**: convert MS Word files to single interim CSV file (Windows-only)
   - **csv2df**: parse interim CSV files and save processed CSV files with annual, quarterly and monthly data

[getter.py](https://github.com/epogrebnyak/mini-kep/blob/master/src/getter.py) is 
an entry point to get parsed data.
   
[mini-kep] is inspired by [FRED](https://fred.stlouisfed.org/) and replaces a predecessor repo,
[data-rosstat-kep](https://github.com/epogrebnyak/data-rosstat-kep), which could not handle vintages of
macroeconomic data well. 

