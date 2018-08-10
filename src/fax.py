"""Check datapoints with checkpoints."""
from kep.util import load_yaml_one_document
from kep.parser.row import Datapoint


def split(string):
    string = string.replace('  ', ' ')
    return string.split(' ')

def to_datapoint(name: str, args: list):
    try:
        freq, year, month, value = args
    except ValueError:
        freq, year, value = args
        month = 12
    return Datapoint(name, freq, int(year), int(month), float(value))

class Validator:
    def __init__(self, filepath):
        self.doc = load_yaml_one_document(filepath)
        
    def mandatory(self):   
        alls = []
        for string in self.doc['all']:
            name, *args = split(string)
            x = to_datapoint(name, args)
            alls.append(x) 
        return alls    
            
    def optional(self):        
        return [[to_datapoint(name, split(s)) for s in strings]
                 for name, strings in self.doc['any'].items()]

def validate(datapoints, filepath):
    v = Validator(filepath)
    checkpoints = v.mandatory()
    require_all(checkpoints, datapoints)
    for checkpoints in v.optional():
        require_any(checkpoints, datapoints)
    print("All values checked")    


class ValidationError(Exception):
    pass        
  
def require_any(checkpoints, datapoints):   
    found = [c for c in checkpoints if c in datapoints]
    if not found:
        raise ValidationError(f'Found none of: {checkpoints}')
    return found    

def require_all(checkpoints, datapoints):   
    for x in checkpoints:
        if x not in datapoints:
            raise ValidationError(f'Required value not found: {x}')
    return checkpoints         
    
