"""Check contents of dataframes with checkpoints"""
import pandas as pd
from kep.util import load_yaml_one_document
from kep.parser.row import Datapoint

def is_in(tseries, dp):
    timestamp = ts(dp.year, dp.month)
    try:
        x = tseries[timestamp]
    except KeyError:
        # timestamp not in tseries index
        return False
    return x == dp.value


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
            
            
                
                
SRC = """
CPI_NONFOOD_rog:
   all:
      - m 1999  1 106.2
      - m 1999 12 101.1
   any:
      - m 1999 12 101.1
      - m 2018  5 100.9
"""


def ts(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()

_df = pd.DataFrame({'CPI_NONFOOD_rog':
                   {ts(1999, 1): 106.2,
                    ts(1999, 2): 104.0,
                       ts(1999, 3): 103.2,
                       ts(1999, 4): 104.0,
                       ts(1999, 5): 102.7,
                       ts(1999, 6): 101.6,
                       ts(1999, 7): 101.9,
                       ts(1999, 8): 102.4,
                       ts(1999, 9): 102.7,
                       ts(1999, 10): 102.2,
                       ts(1999, 11): 101.5,
                       ts(1999, 12): 101.1,
                       ts(2018, 1): 100.3,
                       ts(2018, 2): 100.1,
                       ts(2018, 3): 100.2,
                       ts(2018, 4): 100.4,
                       ts(2018, 5): 100.9,
                       ts(2018, 6): 100.4}})

# dataframes    
dfa, dfq, dfm = _df, _df, _df    
v = Verifier(SRC, dfa, dfq, dfm)
assert v.any()        
assert v.all()        
            
