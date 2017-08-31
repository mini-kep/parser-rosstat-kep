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
# def docstrings(ctx):
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


def apidoc(pkg, exclude=''):
    """Call sphinx-apidoc to document *pkg* package without files
       in *exclude* pattern. """
    rst_source_dir = os.path.join('doc', 'rst')
    pkg_dir = os.path.join('src', pkg)
    flags = '--module-first --no-toc --force'
    return f'sphinx-apidoc {flags} -o {rst_source_dir} {pkg_dir} {exclude}'


@task
def rst(ctx):
    """Build new rst files with sphinx"""
    args_list = [
        ('locations', ''),
        ('download', ''),
        ('word2csv', ''),
        ('csv2df', '*tests*')
        #,('frontpage', '*markdown*')
    ]

    for args in args_list:
        command = apidoc(*args)
        ctx.run(command)


@task
def doc(ctx):
    source_dir = os.path.join('doc', 'rst')
    html_dir = os.path.join('doc', 'html')
    index_html = os.path.join(html_dir, 'index.html')
    # call without parameters
    # for paarmeters may add:
    #     -aE - to overwrite files
    build_command = f'sphinx-build -b html {source_dir} {html_dir}'
    ctx.run(build_command)
    if platform == "win32":
        ctx.run('start {}'.format(index_html))


@task
def test(ctx):
    ctx.run("py.test src")  # --cov=csv2df


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


class PathContext():
    def __init__(self, path=str(Path(__file__).parent / 'src')):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path.remove(self.path)


def _add(year, month):
    year, month = int(year), int(month)

    with PathContext():

        from config import DataFolder

        #download and  unpack
        from download.download import RemoteFile
        remote = RemoteFile(year, month)
        assert remote.download()
        assert remote.unrar()

        # make interim csv from Word files
        interim_csv = DataFolder(year, month).get_interim_csv()
        if not os.path.exists(interim_csv):
            from word2csv.word import make_interim_csv
            assert make_interim_csv(year, month)
            assert DataFolder(year, month).copy_tab_csv()

        #parse, validate, save
        from csv2df.runner import Vintage
        vint = Vintage(year, month)
        assert vint.validate()
        assert vint.save()


@task
def latest(ctx):
    _latest()


def _latest():
    """Copy to latest CSVs and make Excel file."""
    with PathContext():
        # TODO: check the date seems to be latest
        from finaliser import copy_latest
        copy_latest()
        from finaliser import save_xls
        save_xls()


ns = Collection()
for t in [ls, clean,
          pep8, lint,
          test, cov,
          doc, rst,
          add, latest]:
    ns.add_task(t)


# Workaround for Windows execution
if platform == 'win32':
    # This is path to cmd.exe
    ns.configure({'run': {'shell': environ['COMSPEC']}})


if __name__ == '__main__':
    _add(2017, 6)
    print(apidoc('download'))


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
