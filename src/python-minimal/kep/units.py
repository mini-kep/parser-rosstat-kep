from kep.util import load_yaml

__all__ = ['UnitMapper']


def get_units_dict(source: str):
    return load_yaml(source)[0]    

def get_mapper(source: str):
    units_dict = get_units_dict(source)
    return UnitMapper(units_dict)

def to_mapper_dict(listing: dict):    
    return {pat: key for key, values in listing.items() for pat in values}


class UnitMapper:
    """Initialise mapper with *listing* dictionary 
       and use .extract() method to parse text.
    """
    def __init__(self, listing: dict):
        self.mapper_dict = to_mapper_dict(listing)

    def extract(self, text: str)-> str:
        """Extract unit of measurement from *text*. 
        
        Returns:
            str like 'rog' or 'bln_usd 
        """
        found = []
        for pat in self.mapper_dict.keys():
            if pat in text:
                found.append(pat)
        if found:
            # match largest string found
            pat = max(found, key=len)
            return self.mapper_dict[pat]
        return ''

    def __repr__(self):
        return repr(self.mapper_dict)
