DEFAULT_SPEC = None
CHECKPOINTS = None

def get_csv(date):
    from kep.files import locate_csv
    path = locate_csv(date['year'], date['month'])
    return path  
    
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
    
    def save(self, date):
        pass
    
def csv2df(fp, spec):

    return DataFrameHolder(1,2,3)
         