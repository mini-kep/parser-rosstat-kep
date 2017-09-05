# 1 Parser 

## Parser code

- [ ] fixtures for testing code 
- [ ] added varaible transformation to finaliser
- [ ] src/manage.py with init(), rebuild_all() and update() commands
- [ ] in development branch push  download/word2csv/csv2df and finaliser.py one level down to 'make' folder

## Parser paramaters / inputs

- [ ] [#33 Add more variable definitions ](https://github.com/epogrebnyak/mini-kep/issues/33) 	

## Result validation 
  
  - [ ] [full coverage of required variables](https://github.com/epogrebnyak/mini-kep/issues/50)
  - [ ] consistency check

## Parser testing  

  - [ ] see <https://github.com/epogrebnyak/mini-kep/issues?q=is%3Aissue+is%3Aopen+label%3Atesting>
  - [ ] test coverage annotate 
  - [ ] check values from sample rows in spec  
  - [ ] uncomment end-to-end test
  - [ ] review previous testing guidelines    
  - [ ] [CSV mock proposal](https://github.com/epogrebnyak/mini-kep/issues/9)

  
# 2 Frontend / API

Issue <https://github.com/epogrebnyak/mini-kep/issues/18> 

Workfile <https://github.com/epogrebnyak/mini-kep/tree/master/src/frontend>.

Tasks: 
  - [ ] show imported variables or varnames
  - [ ] how many variable were read?

# 3 End-use notebooks

See 'mini-kep-chart' 


      
DONE
====
- [x] helper module with  dates: review **filled_dates** mechanism in files.py 
- [x] [online coverage badge](https://github.com/epogrebnyak/mini-kep/issues/23)
- [x] [simplify procedure to update new month #29](https://github.com/epogrebnyak/mini-kep/issues/29)
- [x] [renaming modules](https://github.com/epogrebnyak/mini-kep/issues/35)
- [x] example.py
- [x] delete from repo: static html
- [x] try ```inv pep8 -f.``` works
- [x] spec.py review
- [x] download an unpack rar files from Rosstat
- [x] helper module with local file paths + maybe also web destination 
- [x] anomalies in ```dfa, dfq, dfm``` revealed <https://github.com/epogrebnyak/mini-kep/issues/63>
- [x] GOV_*_ACCUM differentiated <https://github.com/epogrebnyak/mini-kep/issues/61>  


FLUSHED
=======

s3 sync:
  - workfile <https://github.com/epogrebnyak/mini-kep/blob/master/issues/todo_boto_s3_sync.py>
  - issue: <https://github.com/epogrebnyak/mini-kep/issues/51>
  - [ ] local to S3 
  - [ ] S3 to local 
  - [ ] manually save deeper history of s3 files to bucket

-----------

follow-up tasks from spec.py:
   - [ ] use sample in required
   - [ ] short names for variables in FRED style, ```short=```

---------------

sphinx-doc usage:
  - why modules rst?
  - include intro.md in index.rst
  - warnings in compile
  - hanging kep.rst
  
----------------

document gap (2013, x)

----------------

html docs to bucket:
  - [ ] document why unhappy with readthedocs
  - [x] try restore encoding at readthedocs (maybe python3 issue , will not work)  
  - [ ] uploader to bucket

