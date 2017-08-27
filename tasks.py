# -*- coding: utf-8 -*-
import sys
import os
import inspect

from sys import platform
from os import environ
from pathlib import Path



from invoke import Collection, task


PROJECT_DIR = Path(__file__).parent


def walk_files(directory: Path):
    for _insider in directory.iterdir():
        if _insider.is_dir():
            subs = walk_files(_insider.resolve())
            for _sub in subs:
                yield _sub.resolve()
        else:
            yield _insider.resolve()


def find_all(glob):
    for f in walk_files(PROJECT_DIR):
        if glob in f.name:
            yield f

            
def yield_python_files(folder):
    for file in filter(lambda x: x.suffix == ".py", walk_files(folder)):
        yield file           

            
@task
def pep8(ctx, folder="csv2df"):
    path = PROJECT_DIR / "src" / folder
    for f in yield_python_files(path):
        print("Formatting", f)
        # FIXME: may use 'import autopep8' without console
        ctx.run("autopep8 --aggressive --aggressive --in-place {}".format(f))

# 
#def docstrings(ctx):
#    print(inspect.cleandoc(__doc__))
#    path = PROJECT_DIR / "src" / folder
#    for f in yield_python_files(path):
        # FIXME: list modules as in https://stackoverflow.com/questions/487971/is-there-a-standard-way-to-list-names-of-python-modules-in-a-package
        # print(inspect.cleandoc(__doc__))        
#        pass
       
@task
def clean(ctx):
    """Delete all compiled Python files"""
    for f in find_all(".pyc"):
        print("Removing", f)
        f.unlink()


@task
def lint(ctx, folder="src/csv2df"):
    """Check style with flake8

       See more flake8 usage at:
           https://habrahabr.ru/company/dataart/blog/318776/
    """
    # E501 line too long
    # --max-line-length=100
    ctx.run('flake8 {} --exclude test* --ignore E501'.format(folder))


@task
def rst(ctx):
    # build new rst files with sphinx
    # FIXME: must check / appearance issues:
    
    ctx.run("sphinx-apidoc -efM -o doc src\csv2df *test_*")
    
    
@task
def doc(ctx):
    ctx.run("doc\make.bat html")
    ctx.run("start doc\_build\html\index.html")
    # TODO: 
    # upload all files from doc\_build\html\ 
    # to aws https://mini-kep-docs.s3.amazonaws.com/
    # mini-csv2df-docs + is region neded?


@task
def github(ctx):
    ctx.run("start https://github.com/epogrebnyak/mini-csv2df")


@task
def test(ctx):
    ctx.run("py.test") #--cov=csv2df

# TODO:
# coverage annotate -d csv2df\tests\annotate -i csv2df/runner.py

@task
def cov(ctx):
    ctx.run("py.test --cov=csv2df")
    ctx.run("coverage report --omit=*tests*,*__init__*")


@task
def ls(ctx):
    """List directory"""
    cmd = "dir /b"
    result = ctx.run(cmd, hide=False, warn=True)
    print(result.ok)
    print(result.stdout.splitlines())


@task
def add(ctx, year, month):
    _add(year, month)    
    
def _add(year, month):    
    year, month = int(year), int(month)
    src = str(Path(__file__).parent / 'src')
    sys.path.insert(0, src)
    #download, unpack
    from locations.folder import FolderBase
    from download.download import RemoteFile
    rf = RemoteFile(year, month)
    rf.download()
    rf.unrar()
    interim_csv = FolderBase(year, month).get_interim_csv()
    #make interim csv
    if not os.path.exists(interim_csv):
        from word2csv.word import make_interim_csv
        make_interim_csv(year, month)
        FolderBase(year, month).copy_tab_csv()        
    #parse, validate, save
    from csv2df.runner import Vintage
    vint = Vintage(year, month)
    vint.validate()
    vint.save()
    #copy to latest
    from locations.folder import copy_latest
    copy_latest()
    sys.path.remove(src)
    # see for context manager: 
    # https://stackoverflow.com/questions/17211078/how-to-temporarily-modify-sys-path-in-python


ns = Collection()
for t in [clean, pep8, ls, cov, test, doc, rst, github, lint, add]:
    ns.add_task(t)


# Workaround for Windows execution
if platform == 'win32':
    # This is path to cmd.exe
    ns.configure({'run': {'shell': environ['COMSPEC']}})


if __name__ == '__main__':
    _add(2017, 5)

##########################################################################
# GLOBALS                                                                       #
##########################################################################

# PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
#BUCKET = {{ cookiecutter.s3_bucket }}
#PROFILE = {{ cookiecutter.aws_profile }}
#PROJECT_NAME = {{ cookiecutter.repo_name }}
#PYTHON_INTERPRETER = {{ cookiecutter.python_interpreter }}

##########################################################################
# COMMANDS                                                                      #
##########################################################################

# Make Dataset
#data: requirements
#	$(PYTHON_INTERPRETER) src/data/make_dataset.py


# Upload Data to S3
# sync_data_to_s3:
# ifeq (default,$(PROFILE))
#	aws s3 sync data/ s3://$(BUCKET)/data/
# else
#	aws s3 sync data/ s3://$(BUCKET)/data/ --profile $(PROFILE)
# endif

# Download Data from S3
# sync_data_from_s3:
# ifeq (default,$(PROFILE))
#	aws s3 sync s3://$(BUCKET)/data/ data/
# else
#	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
# endif
