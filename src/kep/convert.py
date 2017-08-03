# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 01:25:34 2017

@author: Евгений
"""
from kep.rows import read_csv
from kep.vintage import Frames 
from kep.tables import get_tables

class DataFrameHolder(object):
    
    def __init__(self, dfa, dfq, dfm):
        self.dfa = dfa
        self.dfq = dfq
        self.dfm = dfm
        
    def annual(self):
        return self.dfa
    
    def quarterly(self):
        return self.dfq
        
    def monthly(self):  
        return self.dfm
    
    def includes(self, x):
        return True 
    
    def get_error_message(self, x):
        return "some error found"
        
    def _all(self):
        yield self.dfa, self.dfq, self.dfm
    
    def save(self, year, month):
        pass

def csv2frames(path, spec, units):
    # rowstack
    _rows = read_csv(path)
    # convert stream values to pandas dataframes
    _tables = get_tables(_rows, spec, units)
    frames = Frames(tables=_tables)
    return DataFrameHolder(*frames.dfs())



            
if __name__ == "__main__":
    from kep import files
    from kep import rows
    from spec import SPEC
    csv_path = files.locate_csv()
    _rows = rows.read_csv(csv_path)
    tables = get_tables(_rows, spec=SPEC)
    for t in tables:
        print()
        print(t)            


