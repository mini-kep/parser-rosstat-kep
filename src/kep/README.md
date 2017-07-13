File roles
==========

### Configuration/inputs:
  - **cfg.py** is parsing definitions, most importanty linking some of strings as varibale names or units of measurement   	
  - **files.py**  allows to abstract csv filepaths by (year, month) 
 
### "Meat":
  - *rows.py* - first layer of abstraction, basic search/manipulation functions on CSV row
  - *tables.py* - parser to split CSV file into Tables() instances 
  - *vintage.py* - emitting values from tables and saving data to ```data/processed``` + wrappers like Collection
  
### Libs: 
  - splitter.py - functions used to parse a rows of different lengths, well covered by doctests, I hope. 		

To see how it works 
===================
Run \_\_main\_\_ part in following scripts and look at some output:
- cfg.py
- tables.py
- vintage.py

Testing status
==============
1. Well tested file is *rows.py* - small clear fixtures, quick tests, can add a bit more coverage
2. Large end-to-end test is *test__checkpoints.py* - makes sure some control values were read
3. Most tests in between not so good:
 - fixtures grow big, "chained" and less understandable
 - things not tested in isolation 
 - different approaches to testing (setup methods, fixtures, dep.injection/mocking)
 - test naming
 - not testing bad egde cases, etc.
 
TODOs
=====
Make new branch/PR for following:
1. Go over **test_rows.py** and make any suggestions about its enhancement (via comments like ```#FIXME EP: must also test .len() method```).
2. Fix <src/kep/tests/test__checkpoints.py ...FFF> by supplying new hardcoded constants
3. Pick some things to fix from  [issues related to testing](https://github.com/epogrebnyak/mini-kep/issues?q=is%3Aissue+is%3Aopen+label%3Atesting),
   approve a plan to fix them, make a fix, refer issue in commits/PR. 
 
 
 
