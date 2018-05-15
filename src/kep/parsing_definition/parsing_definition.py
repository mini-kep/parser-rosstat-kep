"""Parsing definition to identify tables in the data source file.
    
   A defnition contains a list of nested dicts. 

   Each dict has following keys: 
   - commands, a list of dicts each with following keys:     
       - variable name ('GDP')
       - corresponding headers ('Oбъем ВВП')
       - units of measurement ('bln_rub')
   - boundaries (start and end lines of text)   
   - reader function name(string)

"""

from kep.csv2df.util.label import make_label
from kep.parsing_definition.user_data import COMMANDS_DEFAULT, COMMANDS_BY_SEGMENT

from typing import List, Union, Any
StringType = Union[str, List[str]]


def as_list(x: Any):
    """Transform *x* to list *[x]*.

       Returns:
           list
    """
    if isinstance(x, list):
        return x
    elif isinstance(x, tuple):
        return list(x)
    else:
        return [x]


def make_parsing_command(var: str, header: StringType, unit: StringType):
    """Create parsing instructions for an individual variable.

    Keys:
        varname (str):
            varaible name, ex: 'GDP'
        table_headers-strings (list of strings):
            header string(s) associated with variable names
            ex: ['Oбъем ВВП'] or ['Oбъем ВВП', 'Индекс физического объема произведенного ВВП']
        units (list of strings):
            required_labels unit(s) of measurement
            ex: ['bln_usd]' or ['rog', 'rub']
    """
    return dict(varname = var,
                table_headers = as_list(header), 
                required_units = as_list(unit))


def make_super_definition_entry(commands: List[dict] , 
                          boundaries: List[dict] = [], 
                          reader: str = ''):
    # preprocessing
    commands_list = [make_parsing_command(**c) for c in as_list(commands)]
    # control tructure
    return dict(mapper = make_table_header_mapper(commands_list),
                required_labels = make_required_labels(commands_list),
                boundaries = boundaries,
                reader = reader)  


def make_table_header_mapper(commands):
    result = {}
    for c in commands:
        for header in c['table_headers']:
            result[header] = c['varname'] 
    return result

    
def make_required_labels(commands):
    result = []
    for c in commands:
        for unit in c['required_units']:
            result.append(make_label(c['varname'], unit))
    return result

def make_super_parsing_definition_list(default=COMMANDS_DEFAULT,
                                       by_segment=COMMANDS_BY_SEGMENT,
                                       factory=make_super_definition_entry):
    definitions = [factory(default)]
    for segment_dict in by_segment:
        pdef = factory(**segment_dict)        
        definitions.append(pdef)
    return definitions

PARSING_DEFINITIONS = make_super_parsing_definition_list()


from ruamel.yaml import YAML
import sys

yaml=YAML(typ='rt')
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.default_style="'"
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.dump_all(PARSING_DEFINITIONS, sys.stdout)



