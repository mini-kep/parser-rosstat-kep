"""Check contents of dataframes with checkpoints"""
from kep.util import load_yaml_one_document, timestamp
from kep.parser.row import Datapoint



def is_in(tseries, datapoint):
    date = timestamp(datapoint.year, datapoint.month)
    try:
        x = tseries[date]
    except KeyError:
        # timestamp is not in tseries index
        return False
    return x == datapoint.value


def to_datapoint(string: str, name):
    string = string.replace('  ', ' ')
    args = string.split(' ')
    try:
        freq, year, month, value = args
    except ValueError:
        freq, year, value = args
        month = 12
    return Datapoint(name, freq, int(year), int(month), float(value))


def extract(source_dict: dict, freq: str, method: str):
    res = []
    for name, subdict in source_dict.items():
        items = subdict.get(method)
        if items:
            datapoints = [to_datapoint(item, name) for item in items]
            out = [dp for dp in datapoints if dp.freq == freq]
            if out: 
                res.append((name, out))
    return res    


class ValidationError(Exception):
    pass


class Verifier():
    def __init__(self, checkpoint_source, dfa, dfq, dfm):
        self.dfs = dict(a=dfa, q=dfq, m=dfm)
        self.check_dict = load_yaml_one_document(checkpoint_source)

    def checkpoints(self, freq, mode):
        return extract(self.check_dict, freq, mode)
    
    def find(self, freq, mode):
        res = []
        df = self.dfs[freq]
        checkpoints = self.checkpoints(freq, mode)
        for name, values in checkpoints:
            tseries = df[name]
            for value in values:
                x = value, is_in(tseries, value)                
                res.append(x)
        return res        
                
    def zip(self, freq, mode):
        found = self.find(freq, mode)
        return [[x[i] for x in found] for i in [0, 1]] 
    
    def all(self):
        for freq in 'aqm':
            for x, flag in self.find(freq, 'all'):
                if not flag:                    
                    raise ValidationError(f'Required value not found: {x}') 
        return True            
                    
    def any(self):  
        for freq in 'aqm':  
            values, bools = self.zip(freq, 'any')
            if bools and not any(bools):
                raise ValidationError(f'Found none of: {values}')
        return True
  