import pathlib
import yaml
from schema import Schema, Optional, Or, SchemaError

from kep.definition.units import BASE_UNITS, UnitMapper
from kep.label import make_label



class Repr(object):
    def __repr__(self):
        return repr(self.__dict__)

def make_mapper_dict(base_mapper_dict,
                     custom_mapper_dict,
                     units):
    mapper_dict = {k:v for k, v in base_mapper_dict.items() 
                       if v in units}
    for k, v in custom_mapper_dict.items():
        mapper_dict[k] = v 
    return mapper_dict     

    
class Parser(Repr):
    def __init__(self, 
                 name,
                 headers,
                 units=[],
                 custom_mapper_dict={},
                 base_mapper_dict=BASE_UNITS,
                 **kwargs):
        self.name = name
        self.headers = iterate(headers)
        units = iterate(units)
        mapper_dict = make_mapper_dict(base_mapper_dict,
                                       custom_mapper_dict,
                                       units)
        self.mapper = UnitMapper(mapper_dict)
            
    @property        
    def units(self):
         return self.mapper.values()  

    @property        
    def labels(self):
         return [make_label(self.name, x) for x in self.units]


class Scope(Repr):
    ALWAYS_VALID_START_LINE = ''
    def __init__(self, starts=None, ends=None, **kwargs):
        starts = starts if starts else self.ALWAYS_VALID_START_LINE
        self.starts = iterate(starts)
        self.ends = iterate(ends)
        
    def is_defined(self):
        return (self.starts != [self.ALWAYS_VALID_START_LINE] 
                and self.ends != [])

class Namer(Parser):
    def __init__(self, _dict):
        super().__init__(**_dict)
        self.scope = Scope(**_dict)
        self.reader = _dict.get('reader')


def validate_dictionaries(dicts):
    schema = Schema({'name': str, 
                     'headers': Or(str, [str]),
                     'units': Or(str, [str]),
                     Optional('reader'): str,
                     Optional('starts'): Or(str, [str]),
                     Optional('ends'): Or(str, [str])
                     })
    for d in dicts:
        try:
            schema.validate(d)
        except SchemaError:
            raise ValueError(d)


PATH_YAML_NAMER = pathlib.Path(__file__).with_name('namers.txt')

def get_text(path=PATH_YAML_NAMER):
    return path.read_text(encoding='utf-8')    


def get_namers():
    doc = get_text()
    dicts = yaml.load(doc)
    validate_dictionaries(dicts)
    return [Namer(d) for d in dicts]


NAMERS = get_namers()


#    @property
#    def labels(self):
#        returnt sorted([make_label(self.name, unit) for unit in self.units])
#
#    def inspect(self, tables):
#        pass
#        # WONTFIX:
#        # is found header found not more than only once?
#
#    def assert_all_labels_found(self, tables):
#        if self.labels != tables.labels:
#            raise ValueError((self.labels, tables.labels))
#
