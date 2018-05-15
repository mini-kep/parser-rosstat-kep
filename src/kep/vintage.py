"""Extract dataframes by year and month."""

from kep import FREQUENCIES

from kep.parsing_definition import (DEFINITION_DEFAULT, 
                                    DEFINITIONS_BY_SEGMENT, 
                                    UNITS)
from kep.csv2df.allocation import yield_parsing_assignments
from kep.csv2df.parser import evaluate_assignment

from kep.csv2df.dataframe_maker import create_dataframe
from kep.helper.date import Date
from kep.helper.path import InterimCSV, ProcessedCSV


"""
units.py
- UNITS
parsing_definition.py:
- YAML_DEFAULT -> COMMANDS_DEFAULT -> DEFINITION_DEFAULT 
- YAML_BY_SEGMENT -> INSTRUCTIONS_BY_SEGMENT -> DEFINITIONS_BY_SEGMENT

allocation.py and vintage.py
- DEFINITION_DEFAULT + DEFINITIONS_BY_SEGMENT + UNITS + csv_text -> jobs

parser.py and vintage.py:
- jobs -> values

dataframe_maker.py and vintage.py:
- values -> dataframes
"""


#FIXME: validation is ugly 
from kep.validation.checkpoints import (
    CHECKPOINTS,
    OPTIONAL_CHECKPOINTS,
    validate2
)

def yield_values(csv_text: str,
                 units = UNITS,
                 def0 = DEFINITION_DEFAULT, 
                 pdefs = DEFINITIONS_BY_SEGMENT): 
    for a in yield_parsing_assignments(csv_text, units, def0, pdefs):
        for value in evaluate_assignment(a):
            yield value 

class Vintage:
    """Represents dataset release for a given year and month.
    
       Parses interim CSV file and obtains resulting dataframes.
    """
    def __init__(self, year: int, month: int):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        self.values = list(yield_values(csv_text))
        self.dfs = {freq: create_dataframe(self.values, freq) for freq in FREQUENCIES}

    def save(self, folder=None):
        csv_processed = ProcessedCSV(self.year, self.month, folder)
        for freq, df in self.dfs.items():
            path = csv_processed.path(freq)
            # Convert 1524.3999999999996 back to 1524.4
            # Deaccumulation procedure in parser.py responsible  
            # for float number generation. 
            # WONTFIX: the risk is loss of data for exchange rate, 
            #          may need fomatter by column. annual values can be
            #          a guidance for a number of decimal positions.
            df.to_csv(path, float_format='%.2f')
            print("Saved dataframe to", path)

    #FIXME: validation is ugly 
    def validate(self):
        for freq in FREQUENCIES:
            validate2(df=self.dfs[freq],
                      required_checkpoints=CHECKPOINTS[freq],
                      additional_checkpoints=OPTIONAL_CHECKPOINTS[freq],
                      strict=False)
        print("Test values parsed OK for", self)

    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)


# FIXME: too many responsibilities
class Latest(Vintage):
    """Operations on most recent data release."""

    def __init__(self, year: int, month: int):
        # protect from using old releases of data
        Date(year, month).assert_latest()
        super().__init__(year, month)

    def upload(self):
        from parsers.mover.uploader import Uploader
        self.validate()
        # FIXME: possible risk - *self.datapoints* may have different serialisation 
        #        format compared to what Uploader() expects
        #           (a) date format   
        #           (b) extra keys in dictionary
        Uploader(self.datapoints).post()

    def save(self, folder=None):
        ProcessedCSV(self.year, self.month).to_latest()


if __name__ == "__main__": # pragma: no cover
    v = Vintage(2018, 1)
    v.validate()
    v.save()
