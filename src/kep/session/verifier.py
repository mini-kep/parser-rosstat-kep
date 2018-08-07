import pandas as pd
from kep.util import iterate
from kep.parser.row import Datapoint
from kep.session .commands import get_checkpoints


# TODO: check dfa, dfq, dfm with checkpoints_source

def is_in(d: Datapoint, df: pd.DataFrame):
    return 1

class Verifier():
    def init(self, dfa, dfq, dfm):
        self.dfs = dict(a=dfa, q=dfq, m=dfm)
        pass
        # flatten frames withh to_dict()
        
    def all(self, lookup_values):
        """Require all values from strings, raise exception otherwise."""
        for v in lookup_values:
            if not self.is_found(v):
                msg = "Datapoint not found", v #, subset(v, datapoints)
                raise AssertionError(msg)    
    
    def any(self, lookup_values):
        """Require at least one value from strings, raise exception otherwise."""
        bools = [self.if_found(value) for value in lookup_values]
        if not any(bools):         
             d = [(k, v) for k, v in zip(bools, lookup_values)]
             msg = "Datapoints not found", d#, subset(lookup_values[0], datapoints)
             raise AssertionError(msg)    

    def which_df(self, freq):
        return self.dfs[freq]

    def is_found(self, d: Datapoint):
        df = self.which_df(d.freq)
        return is_in(d, df)       
        
    
def verify(checkpoints_source, dfa, dfq, dfm):
    v = Verifier(dfa, dfq, dfm)
    for method, args in get_checkpoints(checkpoints_source):
        x = as_datapoints(args)
        getattr(v, method)(x)

   
# --------------
    
def datapoints(self):
    """Values in parsed tables.
    
    Return:
        list of Datapoint instances"""
    return [x for t in self.parsed_tables for x in t.emit_datapoints()]


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



            
   