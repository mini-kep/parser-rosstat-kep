Objective
=========

Extract data from CSV file using parsing instructions and units of measurement definition. 
Run over monthly data releases to learn about economic indicator revisions.

Inputs
======

- [ ] one CSV file (as `sandbox.CSV_TEXT`)
- [ ] parsing instructions (as `sandbox.INTRUCTIONS_DOC`)
- [ ] default units of measurement (as `sandbox.UNITS_DOC`)

Comment: units of measurement can be a part of parsing instructions, 
         but they are reused often, that is why they are a separate 
         input parameter. 

Output
======

Three pandas dataframes at annual, quarterly and monthly frequencies 
(`dfa`, `dfq`, `dfm`)

    
Pseudocode
==========

1. split incoming CSV file to tables, containign header text lines and data
2. repeat for all given parsing instruction: 
   -  a. apply parsing instructions to limit block of tables 
    - b. apply parsing instructions to table headers in block of tables 
         to obtain variable labels (variable names and units of measurement) 
    - c. check all expected variable labels are found 
    - d. check control values for parsed tables   
    - e. save parsed tables to queue of parsed tables
3. emit datapoints from queue of parsed tables
4. create pandas dataframes by frequency
5. deacculmulate some dataframes


TODOS
=====
- [ ] previous functionality
- [ ] speedup
- [ ] more defintions


FIXME
=====
- [ ] restore download/unpack/convert functionality outside parser
- [ ] get latest month 
- kep.filters has duplicate functions
- must use 'a' as 'm12' in 'fiscal' format
- better check than `assert not dfa.empty`

FINAL USE
=========
- plot deviations between first and last estimate
  - make a special dataframe format
- extend parsing definitions for more variables
- upload to database
- plot everything for one  month
- save xls
- write variable names

DONE
====
- run Session on several CSV files
  - [x] two files in data
  - [x] actual files since 2007
- [x] estimate running time 
- [x] more clear yaml import