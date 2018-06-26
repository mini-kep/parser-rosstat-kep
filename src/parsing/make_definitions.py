"""Parsing definition to identify tables in the data source file.
    
   A defnition contains a list of nested dicts. 

   Each dict has following keys: 
   - commands, a list of dicts each with following keys:     
       - variable name ('GDP')
       - corresponding headers ('Oбъем ВВП')
       - units of measurement ('bln_rub')
   - boundaries (start and end lines of text)   
   - reader function name(string)

Create parsing instructions for an individual variable.

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

from collections import namedtuple
import yaml
from typing import List

from .label import make_label


def iterate(x):
    if isinstance(x, list):
        return x
    elif isinstance(x, (str, dict)):
        return [x]
    else:
        raise TypeError(x)
    

def make_table_header_mapper(commands):
    result = {}
    for c in iterate(commands):
        for header in iterate(c['header']):
            result[header] = c['var'] 
    return result

    
def make_required_labels(commands):
    result = []
    for c in iterate(commands):
        for unit in iterate(c['unit']):
            result.append(make_label(c['var'], unit))
    return result


DefinitionFactory = namedtuple('ParsingDefinition', 
                              ['mapper', 'required_labels', 'boundaries',
                               'units', 'reader']) 

def make_parsing_definition(units,
                            commands: List[dict],
                            boundaries: List[dict] = [],
                            reader: str = ''
                            ):
    return DefinitionFactory(mapper = make_table_header_mapper(commands),
                required_labels = make_required_labels(commands),
                boundaries = boundaries,
                reader = reader,
                units = units)  


def from_yaml(yaml_str):
    return list(yaml.load_all(yaml_str))

def make_default_definition(units, default_yaml):
    commands_default = from_yaml(default_yaml)
    return make_parsing_definition(units, commands_default, boundaries=[], reader='')

def make_segment_definition(units, yaml_by_segment):
    instructions_by_segment = from_yaml(yaml_by_segment) 
    return [make_parsing_definition(units, **instruction) 
            for instruction in instructions_by_segment]     

    

