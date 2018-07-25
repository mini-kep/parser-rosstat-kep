Exctact data from CSV file using parsing instructions and units of measurement definition. 

Inputs
======
    - CSV file (as CSV_TEXT)
    - parsing instructions (as INTRUCTIONS_DOC)
    - default units of measurement (as UNITS_DOC)

Output
======
    - list of parsed tables 
    - each parsed table is assigned with variable name, unit of measirement and row format
    - method to extract data from table
    
Pseudocode
==========

1. split incoming CSV file to tables
2. repeat for all given parsing instruction: 
    a. establish block of tables
        - either all tables in CSV file,  
        - or a subset of tables, if start and end text lines are provided
    b. apply parsing instructions to block of tables
    c. check expected variable names and units of measurement 
       are found in block of tables
    d. save parsed tables to queue
3. emit datapoints from queue of parsed tables
4. check values in from parsed tables (not implemented, todo)
