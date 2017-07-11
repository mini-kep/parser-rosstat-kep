[![Build Status](https://travis-ci.org/epogrebnyak/mini-kep.svg?branch=master)](https://travis-ci.org/epogrebnyak/mini-kep)

Требования к программе
======================

**Пользователь** получает доступ к временным рядам макроэкономических переменных, которые представлены в разрезе год, квартал, месяц. Исходная публикация [здесь](http://www.gks.ru/wps/wcm/connect/rosstat_main/rosstat/ru/statistics/publications/catalog/doc_1140080765391)

Разновидности данных:
 - временные ряды на последнюю дату публикации (latest) 
 - сезонно сглаженные временные ряды на последнюю дату публикации (latest-sa)
 - архивные временные ряды на разлиную дату публикации (vintages)

Пользователь:
- читает данные из файлов формата CSV, которые находятся по постоянной ссылке в интернете, с помощью pandas и R
- создает Jupiter notebooks в Питоне и R для работы с данными 
- скачивает и просматривает файл Excel

Пользователь просматривает: 
- список переменных, организованный по разделам
- названия и описания переменных 
- последние значения и краткую историю изменения переменных на графике 
- сезонно сглаженные ряды вместе с исходными рядами на графике 

Пользователь также получает информацию о времени ближайшей публикации новых данных.

**Администратор**:
- скачивает последний архив данных с сайта Росстата
- распаковывает архив
- конверирует файлы Word в csv
- обновляет данные 

Риски
=====
- неправильно считали данные из файла:
  - вообще не те данные под названием переменной
  - другие виды ошибок
- исходные данные в публикации не в том виде, как надо пользователю
- в публикаци нет нужных переменных (цена на нефть)
- прекращена  публикации или пересмотрен формат  
- исходные и сезонно-сглаженные данные стали размещаться Росстатом в машинночитаемом виде
- непериодическая или ошибочная работа администратора с новыми данными 
- нет более старых историчесикх данных 

Описание последовательности операций
====================================

Исходные данные:
- [ ] store archive publications at AWS S3 in zip/rar (now a local folder)
- [ ] download newest publications from Rosstat web site (now a local folder)
- [ ] unzip/unrar Word files (now done manually)
- [x] convert Word to interim CSV (Windows only with MS Word installed)

Парсинг: 
- [x] parse interim CSV using parsing difinitions to get pandas datafames
- [x] save dataframes as CSV in processed folder (canonical dataset)
- [ ] save latest dataset at stable URL
- [ ] seasonal adjustment 
- [ ] diff transformations
- [ ] use common code to access data in processed folder 

Frontend:
- [ ] obtain variable desciption and grouping
- [ ] plot graphs (sprklines/regular graphs)
- [ ] generate frontend as README.md file 
- [ ] generate html access    

Использование:
- [ ] plot visualisations and comments 
 - in plain code files 
 - in notebooks
- [ ] build forecasting models
- [ ] generate reports (PDF/presentations)


Список дальнейших работ 
=======================
Make *notebook/README.MD*:
- vintages / revisions (make markdown based on MS Word)
- [datalab](https://github.com/epogrebnyak/data-lab) 
- inflation components
- oil vs fx
- bank reserves 
- correlations between detrended variables
- macro assumptions for stress testing 

Прочие комментарии 
==================
- longer (but unmaintainable) version: <https://github.com/epogrebnyak/data-rosstat-kep>

Main idea: 
- [x] parse [MS Word files from Rosstat]() to obtain [pandas dataframes]()
- [ ] do seasonal adjustment on time series 
- [ ] visualise and build forecasting models  

See ```src/word/run_word.py``` for converting Word files to CSV files 
and ```src/kep/parse.py``` for parsing CSV to dataframes.

OUT OF SCOPE:
-  read SEP + update KEP with SEP data  
-  prior to 1999
