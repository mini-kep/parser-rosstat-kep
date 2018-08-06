"""Read YAML file with parsing or verification commands.

Used to read:
   - instructions.txt
   - checkpoints.txt

"""

from kep.util import iterate, make_label, load_yaml
from typing import Union

__all__ = ['read_instructions_for_headers', 
           'read_instructions_for_checkpoints',
           'extract_parameters', 'extract_labels']

ALLOWED_METHODS_PARSING = ['start_with', 'end_with',
                           'var', 'headers', 'units',
                           'force_units', 'force_format', 
                           'trail_down_names']

ALLOWED_METHODS_VERIFICATION = ['all', 'any']


#not tested
def read_instructions_for_checkpoints(source: str):
    return [extract_parameters(command, ALLOWED_METHODS_VERIFICATION) 
            for command in load_yaml(source)[0]]


def read_instructions_for_headers(source: str):
    """Read parsing command blocks from *source*.    
    Return:
        list of blocks, each block is a list of tuples
    """    
    return [[extract_parameters(command, ALLOWED_METHODS_PARSING) 
             for command in block] 
             for block in load_yaml(source)]


def extract_key_value_from_dict(d: dict):
    for method, arg in d.items():
      break
    return method, arg


def extract_parameters(command: Union[str, dict], allowed_commands) -> tuple:
    """Return method and argument from command.
    
    Args:
        A command is a string like 'trail_down_names' 
        or a dictionary like {'name': 'CPI'}
    """ 
    if isinstance(command, str):
        method, arg = command, None
    elif isinstance(command, dict):
        method, arg = extract_key_value_from_dict(command)
    if method not in allowed_commands:
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