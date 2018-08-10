"""Get parsing parameters and checkpoints."""
import pathlib
from collections import OrderedDict
from csv2df.core import get_mapper
from csv2df.verify import Checkpoints 
from csv2df.util import load_yaml_from_file

ME = pathlib.Path(__file__)

def persist(filename):
    return str(ME.parent / 'yaml' / filename)

def read_by_key(filepath, pivot_key):
    """Read dictionaries from YAML file if *pivot_key*in keys."""
    return [x for x in load_yaml_from_file(filepath) if pivot_key in x.keys()]
    

def get_groups(filepath):
    def _key(d):
        return tuple(d)[0]
    items = load_yaml_from_file(filepath)[0]
    return OrderedDict([(_key(x), x[_key(x)]) for x in items])


class ParsingParameters:
    def __init__(self):
        i = persist('instructions.yml')
        self.common_dicts = read_by_key(i, 'name')
        self.segment_dicts = read_by_key(i, 'start_with') 
        self.mapper = get_mapper(persist('base_units.yml'))
        self.grouper = get_groups(persist('groups.yml'))        
        c = persist('checkpoints.yml')
        self.mandatory = Checkpoints(c).mandatory()
        self.optional = Checkpoints(c).optional()
        
## TODO: with Schema assert
#p = ParsingParameters()
#assert p.common_dicts
#assert p.segment_dicts
#assert p.mapper
#assert p.grouper
#assert p.mandatory
#assert p.optional


    