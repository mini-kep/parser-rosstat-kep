
Understanding sphinx
====================

sphinx is great on output, yet confusing to work with. My understanding current 
is the following:

1. There is a directory with .rst files and directory with .html files and other 
web content. In my project they are ```doc/rst``` and ```doc/html```. 
  - ```sphinx-quickstart``` will do a different folder structure for you, but in 
    principle it is the same - one for rst, other html.
    
2. ```index.rst```
  - is one minimal file you need to generate documentation 
  - it has ```.. toctree:: ``` directive to list several files
  - it has other rst content, in my case - parts of github README.md 
  
3. ```conf.py``` allows:
   - tweaking sys.path to be able to actually read the source code 
   - adding markdown parser (I use m2r)
   - adding autodoc extension 
   - changing theme for html
   - changing title for html 
   - many other options
   
4. For rst content:
   - ```autodoc``` directives allow exploring your package/module/class/method/function
   - can include markdown files 
   - QUESTION:  mark mod, class, func references in docstring    
   
5. .rst folder can be populated with ```sphinx-apidoc``` and html files are
    build from .rst files by ```sphinx-build```
    -  ```sphinx-apidoc``` and ```sphinx-build``` are wrapped by MAKEFILE and make.bat
    - I use direct calls to them in ```invoke rst``` and ```invoke doc``` commands in tasks.py
    
    
Links
=====
### Style guides
A good structure for docstrings, even in you are not compiling documentation:
- [Google](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments)
- [Numpy](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#documenting-classes)

### Extensions:
- [autodoc](http://www.sphinx-doc.org/en/stable/ext/autodoc.html)
- [napoleon](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/)

### SO and alike 
- <https://stackoverflow.com/questions/25549321/minimal-working-example-for-package-documentation-using-sphinx-in-python>
- <https://pythonhosted.org/an_example_pypi_project/sphinx.html>

### Examples:
- <https://raw.githubusercontent.com/boto/boto3/develop/docs/source/index.rst>

Notes
=====

3. Default argument values are ugly in documentation, what should be done about it?
- [ ] change something in documentation config? 

> Note: according to [this](https://github.com/sphinx-doc/sphinx/issues/759), 
> [this](https://github.com/sphinx-doc/sphinx/issues/759) and 
> [this](https://github.com/sphinx-doc/sphinx/issues/1806) maybe it is not possible to 
> prevent default value expansion.
 		
4. Your other suggestions to docs improvements
   with aim to use this as reference for a developper 
   working with 'kep' package.
   
Write your github username along with suggestion for this task.
 
