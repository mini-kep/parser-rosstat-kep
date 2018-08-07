"""Check contents of dataframes with checkpoints"""
from kep.util import load_yaml_one_document
from kep.parser.row import Datapoint
from kep.session.commands import  key_value_from_dict


def to_datapoint(string: str, name):
    string = string.replace('  ', ' ')
    args = string.split(' ')
    try:
        freq, year, month, value = args
    except ValueError:
        freq, year, value = args
        month = 12
    return Datapoint(name, freq, int(year), int(month), float(value))

def read_checkpoints(source: str, mode: str):
    dicts = load_yaml_one_document(source)[mode]
    res = []
    for d in dicts:
        name, values = key_value_from_dict(d)
        datapoints = [to_datapoint(v, name) for v in values]        
        res.append(datapoints)
    return res    


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

def check(source: str, datapoints):
    for checkpoints in read_checkpoints(source, 'any'):
        print(require_any(checkpoints, datapoints))
    for checkpoints in read_checkpoints(source, 'all'):
        print(require_all(checkpoints, datapoints))
    



#def is_in(tseries, datapoint):
#    date = timestamp(datapoint.year, datapoint.month)
#    try:
#        x = tseries[date]
#    except KeyError:
#        # timestamp is not in tseries index
#        return False
#    return x == datapoint.value

