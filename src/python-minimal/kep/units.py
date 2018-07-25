def convert(listing_dict):
    return {pat: key for key, values in listing_dict.items()
            for pat in values}


class UnitMapper:
    def __init__(self, listing_dict):
        self.mapper_dict = convert(listing_dict)

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
            # match largest string found
            pat = max(found, key=len)
            return self.mapper_dict[pat]
        return None

    def __repr__(self):
        return repr(self.mapper_dict)

# TODO: make test for 'extract'
#       unit='ytd',
#       row_format='YAQQQQMMMMMMMMMMMM',
#       headers=['период с начала отчетного года в % к соответствующему периоду предыдущего года / period from beginning of reporting year as percent of corresponding period of previous year'],
