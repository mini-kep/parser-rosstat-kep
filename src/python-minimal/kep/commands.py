"""Interpret parsing commands. 

A command is:
-  a string like `'trail_down_names'` 
-  a dictionary like `{'name': 'CPI'}`
"""

from kep.util import iterate, make_label, load_yaml
from typing import Union

__all__ = ['read_instructions', 'extract_parameters', 'extract_labels']

ALLOWED_METHODS = ['start_with', 'end_with',
                    'var', 'headers', 'units',
                    'force_units', 'force_format', 
                    'trail_down_names']


def read_instructions(source: str):
    """Read command blocks from *source*    
    Return:
        list of blocks, each block is a list of tuples
    """    
    return [[extract_parameters(command) for command in block] 
            for block in load_yaml(source)]


def extract_key_value_from_dict(d: dict):
    for method, arg in d.items():
      break
    return method, arg


def extract_parameters(command: Union[str, dict]) -> tuple:
    """Return method and argument from command.""" 
    if isinstance(command, str):
        method, arg = command, None
    elif isinstance(command, dict):
        method, arg = extract_key_value_from_dict(command)
    if method not in ALLOWED_METHODS:
        raise ValueError(method)
    return method, arg    
        
    
def extract_labels(commands: list):
    labels = []
    for command in commands:
        method, arg = command
        if method == 'var':
            name = arg
        elif method in ['units', 'force_units']:
            units = iterate(arg)
            current_labels = [make_label(name, unit) for unit in units]
            labels.extend(current_labels)
    return labels