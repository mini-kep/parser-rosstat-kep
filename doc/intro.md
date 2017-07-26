[mini-kep](https://github.com/epogrebnyak/mini-kep) aims to parse [MS Word files from Rosstat][rosstat]
to obtain pandas dataframes with macroeconomic time series and save clean [processed CSV files at stable URL]. 

[rosstat]:  http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
[latest]: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest

### Parser pipeline

Steps involved in the parsing pipeline are the following:

- **manually** (*FIXME*):

  - download zip/rar file for a specified month [from Rosstat website][rosstat]
  - unpack MS Word files to a local folder

- **word2csv**: convert MS Word files to single interim CSV file (see [example](https://github.com/epogrebnyak/mini-kep/blob/master/data/interim/2017/05/tab.csv))

- **csv2df**: parse interim CSV file to obtain [processed CSV files](https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest) with annual, quarterly and monthly data.

### Additional files 

Also in [/src](https://github.com/epogrebnyak/mini-kep/tree/master/src) folder:

- **access_data**: sample code to download data from stable URL and save a local copy   
- **frontpage**: addind tables and graphs to [README.md](https://github.com/epogrebnyak/mini-kep/blob/master/README.md)


