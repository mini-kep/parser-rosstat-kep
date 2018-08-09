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


def extract_datapoints(doc: dict):    
    return [[to_datapoint(name, split(s)) for s in strings]
             for name, strings in doc.items()] 


def get_checkpoints(filepath):
    doc = load_yaml_one_document(filepath)
    alls = []
    for string in doc['all']:
        name, *args = split(string)
        x = to_datapoint(name, args)
        alls.append(x)    
    anys = extract_datapoints(doc['any'])
    return dict(any_list=anys, all_list=alls)

all_list, any_lists = get_checkpoints('param//checkpoints.yml')


class ValidationError(Exception):
    pass        

def contains_which(checkpoints, datapoints):
    return [c for c in checkpoints if c in datapoints]
   
def require_any(checkpoints, datapoints):   
    found = contains_which(checkpoints, datapoints)
    if not found:
        raise ValidationError(f'Found none of: {checkpoints}')
    return found    

def require_all(checkpoints, datapoints):   
    for x in checkpoints:
        if x not in datapoints:
            raise ValidationError(f'Required value not found: {x}')
    return checkpoints         

def check(datapoints, any_list, all_list):
    for checkpoints in any_list:
        require_any(checkpoints, datapoints)
    require_all(all_list, datapoints)
    print('All checks passed')
    
