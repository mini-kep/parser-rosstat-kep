"""Helper functions."""

import pathlib
import tempfile
import calendar
import os
import yaml


__all__ = ['make_label', 'timestamp', 'load_yaml']


def make_label(name: str, unit: str)-> str:
    """Concat variable name and unit.

    Return:
        str, like 'CPI_rog'
    """
    return '{}_{}'.format(name, unit)


def last_day(year: int, month: int) -> int:
    """Get a number like 28, 29, 30 or 31."""
    return calendar.monthrange(year, month)[1]


def timestamp(year: int, month: int) -> str:
    """Make end of month YYYY-MM-DD timestamp."""
    day = last_day(year, month)
    month = str(month).zfill(2)
    return f'{year}-{month}-{day}'


class TempFile():
    def __init__(self, content: str):
        with tempfile.NamedTemporaryFile() as f:
            self.path = f.name
        self.obj = pathlib.Path(self.path)
        self.obj.write_text(content, encoding='utf-8')

    def __enter__(self):
        return self.path

    def __exit__(self, *args):
        self.obj.unlink()


def exists(filename):
    try:
        return os.path.exists(filename)
    except ValueError:
        return False


def accept_string(func):
    """Treat *filename* a string with file content."""
    def wrapper(source):
        if exists(source):
            return func(source)
        with TempFile(source) as temp_filename:
            return func(temp_filename)
    return wrapper


def read_source(filename: str):
    """Treat *source* as a filename or a string with content."""
    return pathlib.Path(filename).read_text(encoding='utf-8')


def accept_filename(func):
    """Apply *func* to a string or to a filename."""
    def wrapper(source):
        if exists(source):
            source = read_source(source)
        return func(source)
    return wrapper

# FIXME: decorated fucntion docstring not appearing in spynx docs

def load_yaml_from_file(filename: str):
    """Load YAML contents of *doc* string or filename.
       Always return a list. Each list element is a YAML document content.
    """
    doc = read_source(filename)
    return list(yaml.load_all(doc))



@accept_filename
def load_yaml(doc: str):
    """Load YAML contents of *doc* string or filename.
       Always return a list. Each list element is a YAML document content.
    """
    return list(yaml.load_all(doc))


def load_yaml_one_document(doc: str):
    return load_yaml(doc)[0]
