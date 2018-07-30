from kep.util import iterate
from kep.row import Datapoint

def to_datapoint(string: str):
    args = string.split(' ')
    if args[1] == 'a':
        label, freq, year, value = args
        month = 12
    else: 
        label, freq, year, month, value = args
    return Datapoint(label, freq, int(year), int(month), float(value))

 
def as_datapoints(strings: list):
    return [to_datapoint(string) for string in iterate(strings)]


def subset(x, datapoints):
    return [v for v in datapoints if x.label == v.label and x.freq == v.freq]


def require_all(strings, datapoints):
    lookup_values = as_datapoints(strings)
    for v in lookup_values:
        if v not in datapoints:
            msg = "Datapoint not found", v, subset(v, datapoints)
            raise AssertionError(msg)    

def require_any(strings, datapoints):
     lookup_values = as_datapoints(strings)
     bools = [value in datapoints for value in lookup_values]
     if not any(bools):         
         d = [(k, v) for k, v in zip(bools, lookup_values)]
         msg = "Datapoints not found", d, subset(lookup_values[0], datapoints)
         raise AssertionError(msg)
            
   