from csv2df.util import load_yaml_one_document

__all__ = ['UnitMapper', 'get_mapper']


def to_mapper_dict(listing: dict):
    return {pat: key for key, values in listing.items() for pat in values}


class UnitMapper:
    """Initialise mapper with *listing* dictionary
       and use .extract() method to get_parsed_tables text.
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
        return "UnitMapper(%s)" % self.mapper_dict


def get_mapper(source: str)-> UnitMapper:
    """Read mapper for *source* (yaml file or string)."""
    units_dict = load_yaml_one_document(source)
    return UnitMapper(units_dict)
