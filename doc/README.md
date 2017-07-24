DONE
====

```conf.py```:
- ```master_doc = 'index'``` is changeable + can this be ```index.md```?
- ```html_theme = 'haiku'```
- use ```os.path.abspath(".")``` to add current directory to ```sys.path``` in order to make import work 


Understanding sphinx
====================

My goal is to generate API documentation +insert a bit of additional notes that I can use to
guide development process. My program is a parser on a fuzzy csv dump, so I do not target any 
end user, docs are needed to help maintain/modify program. Before sphinx I had hopes for more lightweight tools 
like **pydoc** and **pocco**, which failed for various reasons for me. 

sphinx is a great tool, but it is a bit complicated to start. I thought that I can better understand how to use it if I 
separate the workflow into minimal steps/concepts and ask for comments. Various parts of these steps/concepts
are in documentation, but not explicitly at first sight:

1. There is a directory with instructions and output directory with html (aha, separate model and view!)
2. Instructions directory contains at least ```conf.py``` and ```index.rst```
3. ```index.rst``` contains ```.. toctree:: ``` directive to listing several files. ```toctree``` will link them as contents and allow
links for one to another
4. ```autodoc``` directives allow exploring your package/module/class/method/function API
5. Most of this work can be done by ```sphinx-apidoc``` and ```sphinx-build``` commands.


<https://stackoverflow.com/questions/25549321/minimal-working-example-for-package-documentation-using-sphinx-in-python>


IDEAS
=====

Ideas for parsing intro:
- sample - csv input text + final dataframe
- all in ```__init__.py```
- glossary?

Ideas for intro:
- word2csv
- csv2df: reader + utils + files + reader with Splitter class
- access_sample
- frontpage

Links
=====
### Style guides
A good structure for docstrings, even in you are not compiling documentation:
- [Google](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments)
- [Numpy](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#documenting-classes)

### Extensions:
- [autodoc](http://www.sphinx-doc.org/en/stable/ext/autodoc.html)
- [napoleon](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/)

### Examples:
- <https://raw.githubusercontent.com/boto/boto3/develop/docs/source/index.rst>

TODO
====

I look at ```\mini-kep\doc\_build\html``` for generated documentation 
and do not like what I see too much. 

Areas for improvement:

1. Change appearance of index.html
- [ ] add some text and highlighted code example
- [ ] change what is displayed on a sidebar
- [ ] change order modules listed - manualy select files 

> Done through editing of index.rst
> Better separate files for modules or one?

2. Module docstrings
-  [ ] there are module docstrings, but they do not appear in documentation.
        What should be done about to see them in documentation?

> Maybe some parameters in autodoc module directives.

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
 
