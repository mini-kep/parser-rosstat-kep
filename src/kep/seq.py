#FIXME - mover to parser
#class Seq(list):
#    """list-like class to diagnose duplicate entries"""
#    
#    def __init__(self, *items):
#        # *items* must be a list
#        list.__init__(self, *items)
#        
#    def has_duplicates(self):
#        return len(self.duplicates) > 0 
#    
#    @property
#    def duplicates(self):
#        __occurences__ = {x:self.count(x) for x in self} 
#        return [k for k,v in __occurences__.items() if v>1]
#    
#    @property
#    def unique(self):
#        return sorted(list(set(self))) 

def duplicates(*items):
    z = list(*items)
    __occurences__ = {x:z.count(x) for x in z} 
    return [k for k,v in __occurences__.items() if v>1]

def unique(*items):
    self = list(*items)
    return sorted(list(set(self)))    
    
