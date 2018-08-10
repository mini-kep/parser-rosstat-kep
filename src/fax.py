"""Check datapoints with control values."""
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

class Checkpoints:
    """Read YAML file and provide mandatory and optional sets of checkpoints.""" 
    def __init__(self, filepath):
        self.doc = load_yaml_one_document(filepath)
        
    def mandatory(self):   
        """Return list of Datapoint instances."""
        alls = []
        for string in self.doc['all']:
            name, *args = split(string)
            x = to_datapoint(name, args)
            alls.append(x) 
        return alls    
            
    def optional(self):        
        """Return list of lists of Datapoint instances.
           Will require at least one value from each list."""
        anys = []   
        for name, strings in self.doc['any'].items():
            x = [to_datapoint(name, split(s)) for s in strings]
            anys.append(x)
        return anys

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

def get_checkpoints(filepath):
    v = Checkpoints(filepath)
    return v.mandatory(), v.optional()

def validate(datapoints, checkpoints, optional_lists):
    """Check datapoints with control values found in YAML file at *filepath*.
       Raise ValidationError on error.
    """
    require_all(checkpoints, datapoints)
    for _checkpoints in optional_lists:
        require_any(_checkpoints, datapoints)
    # TODO: show how many of time series are covered     
    print("All values checked")  