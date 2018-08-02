"""Interpret parsing commands. 

A command is a string like `'trail_down_names'` or a dictionary like `{'name': 'CPI'}`
"""

from kep.util import iterate, make_label


__all__ = ['extract_parameters', 'extract_labels']


def extract_key_value_from_dict(d: dict):
    for method, arg in d.items():
      break
    return method, arg


def extract_parameters(command):
    if isinstance(command, str):
        return command, None
    elif isinstance(command, dict):
        return extract_key_value_from_dict(command)
    
def extract_labels(commands: list):
    for command in commands:
        method, arg = extract_parameters(command)
        if method == 'var':
            name = arg
        elif method in ['units', 'force_units']:
            units = iterate(arg)
    return [make_label(name, unit) for unit in units]