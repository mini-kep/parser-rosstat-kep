# -*- coding: utf-8 -*-
import sys
import os

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
def pep8(ctx, folder=''):
    path = PROJECT_DIR / 'src' / folder
    for f in yield_python_files(path):
        print("Formatting", f)
        # FIXME: may use 'import autopep8' without console
        ctx.run("autopep8 --aggressive --aggressive --in-place {}".format(f))


@task
def clean(ctx):
    """Delete all compiled Python files"""
    for f in find_all(".pyc"):
        print("Removing", f)
        f.unlink()
    # TODO: delete __pycache__ folders    


@task
def lint(ctx, folder="src/csv2df"):
    """Check style with flake8

       See more flake8 usage at:
           https://habrahabr.ru/company/dataart/blog/318776/
    """
    # E501 line too long
    # --max-line-length=100
    ctx.run('flake8 {} --exclude tests* --ignore E501'.format(folder))

# documentation 

def apidoc(subpkg=None, exclude=''):
    """Call sphinx-apidoc to document *pkg* package without files
       in *exclude* pattern. """
    rst_source_dir = os.path.join('doc', 'rst')    
    pkg_dir = 'src'
    if subpkg is not None:
        pkg_dir = os.path.join('src', subpkg)
    flags = '--module-first --no-toc --force' 
    return f'sphinx-apidoc {flags} -o {rst_source_dir} {pkg_dir} {exclude}'


@task
def rst(ctx):
    """Build new rst files with sphinx-apidoc"""
    command = apidoc(exclude='*tests* *example*')
    ctx.run(command)


@task
def doc(ctx):
    source_dir = os.path.join('doc', 'rst')
    html_dir = os.path.join('doc', 'html')
    index_html = os.path.join(html_dir, 'index.html')
    build_command = f'sphinx-build -b html {source_dir} {html_dir}'
    ctx.run(build_command)
    if platform == "win32":
        ctx.run('start {}'.format(index_html))


@task
def find(ctx, regex):
    exclude = """ -name "*.py" ! -name "__init__.py" ! -name "tests*" """
    command = ' | '.join([f"find . -type f {exclude}"
                        , f"xargs grep -nH '{regex}'"])
    ctx.run(command)
    

@task
def test(ctx):
    ctx.run("py.tests src --doctest-modules")  # --cov=csv2df


@task
def cov(ctx):
    ctx.run("py.test src/python-minimal/test_reader.py src/python/tests/")
    ctx.run("coverage report --include=src/* --omit=*/__init__.py,*/test_*")


@task
def ls(ctx):
    """List directory"""
    cmd = "dir /b"
    result = ctx.run(cmd, hide=False, warn=True)
    print(result.ok)
    print(result.stdout.splitlines())


@task
def add(ctx, year, month):
    year, month = int(year), int(month)
    with PathContext():
        import manage
        manage.run(year, month)


class PathContext():    
    path=str(Path(__file__).parent / 'src')
    
    def __init__(self):
        pass

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path.remove(self.path)


ns = Collection()
for t in [ls, clean,
          pep8, lint,
          test, cov,
          doc, rst,
          find,
          add]:
    ns.add_task(t)


# Workaround for Windows execution
if platform == 'win32':
    # This is path to cmd.exe
    ns.configure({'run': {'shell': environ['COMSPEC']}})


if __name__ == '__main__':
    pass
