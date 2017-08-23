Glossary
========

(in order of appearance)

Rosstat KEP publication
   Monthly publication of macroeconomic time series by Rosstat.
   Released as several MS Word files at Rosstat web site at this link:
   http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391
   

Parsing specification
   Set of instructions used to extract data from CSV file. These instructions link 
   table headers to variable names and units of measurement.

Resulting dataframes
   Pandas dataframes with parsing result, usually denoted as ``dfa, dfq, dfm``.
   They hold time series at annual, quarterly and monthly frequency, respectively.

Stable URL
   Location of a canonical dataset, by time series frequency: 
   
      -  https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest/dfa.csv
      -  https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest/dfq.csv
      -  https://github.com/epogrebnyak/mini-kep/tree/master/data/processed/latest/dfm.csv
