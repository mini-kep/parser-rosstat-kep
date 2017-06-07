[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep)

Main idea: 
- [x] parse [MS Word files from Rosstat]() to obtain [pandas dataframes]()
- [ ] do seasonal adjustment on time series 
- [ ] visualise and build forecasting models  

See ```src/word/run_word.py``` for converting Word files to CSV files 
and ```src/kep/parse.py``` for parsing CSV to dataframes.

Tentative pipline:
- [ ] store archive publications at AWS S3 in zip/rar (now a local folder)
- [ ] download newest publications from Rosstat web site (now a local folder)
- [ ] unzip/unrar Word files (now done manually)
- [x] convert Word to interim CSV (Windows only with MS Word installed)
- [x] parse interim CSV using parsing difinitions to get pandas datafames
- [x] save dataframes as CSV in processed folder (canonical dataset)
- [ ] seasonal adjustment and diff transformations
- [ ] use common code to access data in processed folder 
- [ ] plot visualisations and comments in notebooks
- [ ] generate frontend as README.md file 
- [ ] build forecasting models
- [ ] generate reports (PDF/presentations)

Notes:
- longer (but unmaintainable) version: <https://github.com/epogrebnyak/data-rosstat-kep>
