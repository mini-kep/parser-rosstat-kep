class UnitMapper:
    def __init__(self, long_mapper_dict):
        _items = long_mapper_dict.items() 
        self.mapper_dict = {pat: key for key, values in _items for pat in values}        
            
    def keys(self):
        return self.mapper_dict.keys()

    def values(self):
        values = self.mapper_dict.values()
        return list(set(values))

    def extract(self, text):
        found = []
        for pat in self.mapper_dict.keys():             
             if pat in text:
                 found.append(pat)
        if found:
            # match larger string
            print(found)
            pat = max(found, key=len)
            return self.mapper_dict[pat]
        return None
    
    def __repr__(self):
        return repr(self.mapper_dict)     
    
#       unit='ytd',
#       row_format='YAQQQQMMMMMMMMMMMM',
#       headers=['период с начала отчетного года в % к соответствующему периоду предыдущего года / period from beginning of reporting year as percent of corresponding period of previous year'],    
