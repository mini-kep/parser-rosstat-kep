"""Helper functions."""

import pathlib
import tempfile   
import calendar
import os
import yaml


__all__ =  ['accept_filename_or_content_string',
            'make_label', 'iterate', 'timestamp', 
            'load_yaml']


def make_label(name: str, unit: str)-> str:
    """Concat variable name and unit.
    
    Return: 
        str, like 'CPI_rog'
    """
    return '{}_{}'.format(name, unit)


def iterate(x)-> list:
    """Mask string as [x] list."""
    if isinstance(x, str):
        return [x]
    else:
        return x


def last_day(year: int, month: int) -> int:
    """Get a number like 28, 29, 30 or 31."""
    return calendar.monthrange(year, month)[1]


def timestamp(year: int, month: int) -> str:
    """Make end of month YYYY-MM-DD timestamp."""
    day = last_day(year, month)
    return f'{year}-{str(month).zfill(2)}-{day}'
 

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

def accept_string_parameter(func):
    """Treat *filename* a string with file content."""
    def _wrapper(filename):
        if exists(filename):
            return func(filename)
        with TempFile(filename) as temp_filename:
            return func(temp_filename)
    return _wrapper        
               


def _expect_types(x, types):
    """Enforce x is any of types."""
    if not any([isinstance(x, t) for t in types]):
        annotation = ', '.join([t.__name__ for t in types])
        raise TypeError("expected types %s" % annotation + 
                        ", got type %s" % type(x).__name__)   




    
def _read_source(source: str):
    """Treat *source* as a filename or a string with content."""
    def exists(filename):
        try:
            return os.path.exists(filename)
        except ValueError:
            return False
    _expect_types(source, [str])     
    if exists(source):
        return pathlib.Path(source).read_text(encoding='utf-8')
    return source 


def accept_filename_or_content_string(func):
    """Apply *func* to a string with content or to a filename."""
    def wrapper(source):
        return func(_read_source(source))
    return wrapper

#FIXME: decorated fucntion docstring not appearing in spynx docs.
@accept_filename_or_content_string
def load_yaml(doc: str):
    """Load YAML contents of *doc* string or filename.    
       Always return a list. Each list element is a YAML document content.        
    """
    return list(yaml.load_all(doc))