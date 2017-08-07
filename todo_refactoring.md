Intent: document and test current stable version (found in *master* branch)

By module do:
 - (optional) propose/discuss/commit/eye review changes to code  
 - write assert statements and edit/enhance tests
 - edit module docstrings:
   - module
   - classes, public methods and functions used in other parts of the program
   - other docstrings/comments where needed
 - code examples for documentation where needed  
 - make list of refactoring / enhancements by writing TODO and FIXME in code 
 
For docstrings we use <https://google.github.io/styleguide/pyguide.html#Comments>. 

For testing we use py.test and make follwoing kinds of tests depending on situation:
 - unit tests:
   - a dumb tests with no control values to make sure a method is callable (like for ```__repr__()```), 
   - unit test with simple control values for a small fucntion / method, ususally public ones 
 - behaviour tests with fixtures / mocks for larger functionalities
 - end-to-end test on sample or real data  

Finished work example: **kep.files**:
- code: <https://github.com/epogrebnyak/mini-kep/blob/master/src/kep/files.py>
- test: https://github.com/epogrebnyak/mini-kep/blob/master/src/kep/tests/test_files.py
- rst: <https://github.com/epogrebnyak/mini-kep/blob/master/doc/kep.files.rst>
- documentation: <http://mini-kep-docs.s3-website-eu-west-1.amazonaws.com/kep.files.html>
