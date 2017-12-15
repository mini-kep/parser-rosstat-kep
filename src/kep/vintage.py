"""Get pandas dataframes for a given data and month.

*get_dataframes(path, parsing_definitions)*

*Vintage* class addresses dataset by year and month:

    Vintage(year, month).save()
    Vintage(year, month).validate()

*Collection* manipulates all datasets, released at various dates:

    Collection.save_all()
    Collection.approve_all()
"""
from kep.config import InterimCSV, ProcessedCSV, SUPPORTED_DATES
from kep.definitions.definitions import PARSING_DEFINITIONS
from kep.csv2df.reader import get_segment_with_pdef
from kep.csv2df.parser import extract_tables
from kep.csv2df.emitter import Emitter
from kep.checkpoints import CHECKPOINTS

FREQUENCIES = ['a', 'q', 'm']


def isin(checkpoints, df):   
     def is_found(df, d):
        dt = d['date']
        colname = d['name']
        x = d['value']
        try:
            return df.loc[dt, colname].iloc[0] == x
        except KeyError:
            return False
     return [is_found(df, c) for c in checkpoints]          

class Frame:
    def __init__(self, year, month, parsing_definitions=PARSING_DEFINITIONS):
        self.dfs = get_dataframes(year, month, parsing_definitions)
        
    def isin(self, freq, checkpoints):        
        return isin(checkpoints, self.dfs[freq]) 
    
    def annual(self):
        return self.dfs['a']

    def quarterly(self):
        return self.dfs['q']

    def monthly(self):
        return self.dfs['m']


def get_dataframes(year, month, parsing_definitions=PARSING_DEFINITIONS):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Args:
       path (str) - path to CSV file 
       parsing_defintions - list of Def() instances

    Returns:
       Three pandas dataframes at annual, qtr and monthly frequencies
       in a dictionary.
    """    
    path = InterimCSV(year, month).path
    if not isinstance(parsing_definitions, list):
        parsing_definitions = [parsing_definitions]
    jobs = get_segment_with_pdef(path, parsing_definitions)
    tables = [t for csv_segment, pdef in jobs
                for t in extract_tables(csv_segment, pdef)]
    emitter = Emitter(tables)
    return {freq: emitter.get_dataframe(freq) for freq in FREQUENCIES}


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year, month):
        self.year, self.month = year, month
        self.dfs = get_dataframes(year, month)

    def save(self):        
        csv_processed = ProcessedCSV(self.year, self.month)
        for freq, df in self.dfs.items():
            path = csv_processed.path(freq)
            df.to_csv(path)
            print("Saved dataframe to", path)
        return True

    def validate(self):
        for freq in FREQUENCIES:
            df = self.dfs[freq]
            checkpoints = CHECKPOINTS[freq]
            flags = isin(checkpoints, df)
            if not all(flags):
                missed_points = [c for f, c in zip(flags, checkpoints) if not f]
                raise ValueError(missed_points )
        print("Test values parsed OK for", self)
        return True
    
    def upload(self, password):
        # TODO: uplaod to databse
        pass
    
    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)


class Collection:
    """Methods to manipulate entire set of data releases."""

    def save_all():
        for year, month in SUPPORTED_DATES:
            Vintage(year, month).save()

    def approve_all():
        """Checks all dates, runs for about 1-2 min of a fast computer.
           May fail if dataset not complete, eg word2csv written only part
           of CSV file.
        """
        for year, month in SUPPORTED_DATES:
            print("Checking", year, month)
            vintage = Vintage(year, month)
            vintage.validate()


if __name__ == "__main__":
    # Collection.approve_all()
    # Collection.save_all()

    # sample Vintage call
    year, month = 2017, 10
    vint = Vintage(year, month)
    vint.validate()
    dfa, dfq, dfm = [vint.dfs[freq] for freq in 'aqm']