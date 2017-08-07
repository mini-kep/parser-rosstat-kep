# -*- coding: utf-8 -*-
from sys import platform
from os import environ
from invoke import Collection, task
from pathlib import Path


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


@task
def pep8(ctx, folder="kep"):
    path = PROJECT_DIR / "src" / folder
    files = filter(lambda x: x.suffix == ".py", walk_files(path))
    for f in files:
        print("Formatting", f)
        # FIXME: may use 'import autopep8' without console
        ctx.run("autopep8 --aggressive --aggressive --in-place {}".format(f))


@task
def clean(ctx):
    """Delete all compiled Python files"""
    for f in find_all(".pyc"):
        print("Removing", f)
        f.unlink()


@task
def lint(ctx, folder="src/kep"):
    """Check style with flake8

       See more flake8 usage at:
           https://habrahabr.ru/company/dataart/blog/318776/
    """
    # E501 line too long
    # --max-line-length=100
    ctx.run('flake8 {} --exclude test* --ignore E501'.format(folder))


@task
def rst(ctx):
    # TODO:
    # build new modules sphinx
    # sphinx-apidoc -feM -o. ../src/kep
    pass


@task
def doc(ctx):
    ctx.run("doc\make.bat html")
    ctx.run("start doc\_build\html\index.html")
    # TODO: 
    # upload all files from doc\_build\html\ 
    # to aws https://mini-kep-docs.s3.amazonaws.com/
    # mini-kep-docs + is region neded?


@task
def github(ctx):
    ctx.run("start https://github.com/epogrebnyak/mini-kep")


@task
def issues(ctx): 
    pass
    # NOT TODO NOW: open a new issueon github
    # https://github.com/epogrebnyak/mini-kep/issues/new
    # https://gist.github.com/JeffPaine/3145490    


@task
def test(ctx):
    ctx.run("py.test --cov=kep")


@task
def cov(ctx):
    ctx.run("coverage report --omit=*tests*")


@task
def ls(ctx):
    """List directory"""
    cmd = "dir /b"
    result = ctx.run(cmd, hide=False, warn=True)
    print(result.ok)
    print(result.stdout.splitlines())


ns = Collection()
for t in [clean, pep8, ls, cov, test, doc, rst, github]:
    ns.add_task(t)


# Workaround for Windows execution
if platform == 'win32':
    # This is path to cmd.exe
    ns.configure({'run': {'shell': environ['COMSPEC']}})


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
