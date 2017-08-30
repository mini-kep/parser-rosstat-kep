[mini-kep] parses MS Word files from [Rosstat KEP publication][Rosstat], 
creates pandas dataframes with macroeconomic time series 
and saves them as [CSV files at stable URL][backend]. 

  [mini-kep]: https://github.com/epogrebnyak/mini-kep
  [Rosstat]: http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
  [backend]: https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest

[mini-kep] code has following packages:
   - **locations**: navigate through repo directory structure 
   - **download**: download and unpack rar files from Rosstat website
   - **word2csv**: convert MS Word files to single interim CSV file (Windows-only)
   - **csv2df**: parse interim CSV files and save processed CSV files with annual, quarterly and monthly data

helped by:       
   - **frontpage**: generate png graphs and markdown tables