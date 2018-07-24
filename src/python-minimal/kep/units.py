from kep.util import read_yaml

class UnitMapper:
    def __init__(self, mapper_dict):
        self.mapper_dict = mapper_dict
        
    def append(self, mapper_dict):
        for k, v in mapper_dict.items():
            self.mapper_dict[k] = v
            
    def keys(self):
        return self.mapper_dict.keys()

    def values(self):
        values = self.mapper_dict.values()
        return list(set(values))

    def extract(self, text):
        for pat in self.mapper_dict.keys():
             if pat in text:
                 return self.mapper_dict[pat]
        return None
    
    def __repr__(self):
        return repr(self.mapper_dict)
        

def read_base_units(filename='base_units.txt'):
    base_doc = read_yaml(filename)
    return {pat: key for key, values in base_doc.items() for pat in values}

BASE_UNITS = read_base_units()