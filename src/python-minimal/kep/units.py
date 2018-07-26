def convert(listing_dict):
    return {pat: key for key, values in listing_dict.items()
            for pat in values}


class UnitMapper:
    """Initialise mapper with *listing_dict* dictionary and use .extract() 
       method to parse units of measurements for headers.
    """
    def __init__(self, listing_dict):
        self.mapper_dict = convert(listing_dict)

    def extract(self, text):
        found = []
        for pat in self.mapper_dict.keys():
            if pat in text:
                found.append(pat)
        if found:
            # match largest string found
            pat = max(found, key=len)
            return self.mapper_dict[pat]
        return None

    def __repr__(self):
        return repr(self.mapper_dict)
