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
from kep.validator import validate


FREQUENCIES = ['a', 'q', 'm']

def from_year(year):
    return f'{year}-12-31'

def from_month(year, month):
    return f'{year}-{month}'

def from_qtr(year, qtr):
    month = qtr * 3
    return from_month(year, month)


# NOTE: Frame will superseed Vintage

class Frame:
    def __init__(self, year, month, parsing_definitions=PARSING_DEFINITIONS):
        self.dfs = get_dataframes(year, month, parsing_definitions)
        
    @staticmethod    
    def to_dict(freq: str, t: tuple):
        if freq == 'a':
            date_picker = lambda x: from_year(x[1])
        elif freq == 'q':
            date_picker = lambda x: from_qtr(x[1], x[2])
        elif freq == 'm':
            date_picker = lambda x: from_month(x[1], x[2])
        return dict(colname=t[0], date=date_picker(t), value=t[-1]) 
    
    @staticmethod
    def is_found(df, d):
        colname = d['colname']
        dt = d['date']
        try:
            flag = df.loc[dt, colname] == d['value']
        except KeyError:
            flag = False
        try:
            #FIXME: consume a part of dataframe
            return all(flag)
        except TypeError:
            return flag
        
    def isin(self, freq, checkpoints):
        normalised_checkpoints = [self.to_dict(freq, t) for t in checkpoints]
        return [self.is_found(self.dfs[freq], t) for t in normalised_checkpoints]
    
    def __getattr__(self, x):
         return self.dfs[x]

def get_dataframes(year, month, parsing_definitions=PARSING_DEFINITIONS):
    path = InterimCSV(year, month).path
    return get_dataframes_from_path(path, parsing_definitions)

def get_dataframes_from_path(path, parsing_definitions):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Args:
       path (str) - path to CSV file 
       parsing_defintions - list of Def() instances

    Returns:
       Three pandas dataframes at annual, qtr and monthly frequencies
       in a dictionary.
    """    
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
        validate(self.dfs)
        print("Test values parsed OK for", self)
        return True

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