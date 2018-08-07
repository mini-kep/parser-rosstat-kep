"""Read YAML file with parsing or verification commands.

Used to read:
   - instructions.txt
   - checkpoints.txt

"""

from kep.util import iterate, make_label, load_yaml, load_yaml_one_document
from typing import Union

__all__ = ['get_instructions', 'get_checkpoints']

ALLOWED_METHODS_PARSING = ['start_with', 'end_with',
                           'var', 'headers', 'units',
                           'force_units', 'force_format', 
                           'trail_down_names']

ALLOWED_METHODS_VERIFICATION = ['all', 'any']



def get_checkpoints(source: str):
    commands = load_yaml_one_document(source)
    return make_parameter_list(commands, ALLOWED_METHODS_VERIFICATION)


def get_instructions(source: str):
    """Read parsing command blocks from *source*.    
    Return:
        list of blocks, each block is a list of tuples
    """    
    return [CommandBlock(document) for document in load_yaml(source)]


class CommandBlock:
    def __init__(self, commands):
        self.commands = make_parameter_list(commands, ALLOWED_METHODS_PARSING)      
    @property
    def expected_labels(self):
        return extract_labels(self.commands)

        

def make_parameter_list(commands, allowed_methods):
    return [extract_parameters(command, allowed_methods) for command in commands]


def extract_parameters(command: Union[str, dict], allowed_commands) -> tuple:
    """Return method and argument from command.
    
    Args:
        A command is a string like 'trail_down_names' 
        or a dictionary like {'name': 'CPI'}
    """ 
    if isinstance(command, str):
        method, arg = command, None
    elif isinstance(command, dict):
        method, arg = key_value_from_dict(command)
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

def key_value_from_dict(d: dict):
    for method, arg in d.items():
      break
    return method, arg

