Exctact data from CSV file using parsing instructions and units of measurement definition. 

Inputs
======
    - CSV file (as sandbox.CSV_TEXT)
    - parsing instructions (as sandbox.INTRUCTIONS_DOC)
    - default units of measurement (as sandbox.UNITS_DOC)

Output
======
    - pandas dataframes at three frequencies (dfa, dfq, dfm)
    
Pseudocode
==========

1. split incoming CSV file to tables
2. repeat for all given parsing instruction: 
    a. apply parsing instructions to block of tables
    b. check all expected variable labels (names and units of measurement) 
       are found 
    c. save parsed tables to queue
3. emit datapoints from queue of parsed tables
4. create pandas dataframes
5. check values in from parsed tables

TODOS
=====
- run Session on several CSV files
  - two files in data
  - actual files sinse 2007
- restore download/unpack/convert functionality outside parser
- restore value check procedure
- time running time 
- plot deviations between first and last estimate
- extend parsing definitions for more variables
- upload to database
- check coverage report 
- compeltion metrics - how many variables - see how many variable are parsed

