TODOs
=====
###  test_rows.py : 
- [ ] go over test_rows.py and make any suggestions about its 
      enhancement (via comments like ```#FIXME AB: must also test .len() method```). 
	  test_rows.py is well tested, so this is to train the workflow (make new branch/PRs, commit comments, etc)

###  Todos in spec.py
- [ ] make test_spec.py based on asserts 

###  More planning:
- [ ] in vintage.py need reporting about what has been read + latest values as in readme.md
- [ ] frontpage reporting + graphs
- [+] Fix <src/kep/tests/test\_\_checkpoints.py ...FFF> by supplying new hardcoded constants
- [ ] extend contol values for datapoints ```value=dict(dt="1999-12-31", rog=dict(a=0, q=0, m=0))```
- [ ] pick from [issues related to testing](https://github.com/epogrebnyak/mini-kep/issues?q=is%3Aissue+is%3Aopen+label%3Atesting), approve a plan to fix them +  see below in testing status

### Not todo:
- [ ] split vintage.py into emitter and wrapper



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
2. Large end-to-end test is *test__checkpoints.py** - makes sure some control values were read
3. Most tests in between not so good:
 - fixtures grow big, "chained" and less understandable
 - things not tested in isolation 
 - different approaches to testing (setup methods, fixtures, dep.injection/mocking)
 - test naming
 - not testing bad egde cases, etc.
 

 
 
