"""Read YAML files."""
import yaml
import pathlib
import os

all = ['load_yaml']

def expect_string(x):
    if not isinstance(x, str):
        raise TypeError("expected str not %s" % type(x).__name__)   

def exists(filename):
    try:
        return os.path.exists(filename)
    except ValueError:
        return False
        
    
def accept_filename_or_string(func):
    def wrapper(incoming: str):
        """Treat *incoming* as a filename or string."""
        expect_string(incoming)     
        if exists(incoming):
            doc = pathlib.Path(incoming).read_text(encoding='utf-8')
        else:
            doc = incoming 
        return func(doc)    
    return wrapper  

@accept_filename_or_string
def load_yaml(doc: str):
    """Load yaml contents of *doc* string or filename."""
    try:
        return yaml.load(doc)
    except yaml.YAMLError:
        return list(yaml.load_all(doc))







 

