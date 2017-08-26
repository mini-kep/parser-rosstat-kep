"""Get pandas dataframes for a given data and month. 

*get_dataframes(csvfile, spec=SPEC)* is a lower-level function to get 
dataframes from *csvfile* connection under *spec* parsing instruction.  

*Vintage* class addresses dataset by year and month:

    Vintage(year, month).save()
    Vintage(year, month).validate()

These calls should give similar results:
    
    csv_path = PathHelper.locate_csv(year, month)
    csvfile = open_csv(csv_path)
    
    Vintage(year, month).dfs()

*Collection* manipulates all datasets, released at various dates:

    Collection.save_all()
    Collection.save_latest()
    Collection.approve_latest()
    Collection.approve_all()
"""

from csv2df.helpers import DateHelper, PathHelper
from csv2df.specification import SPEC
from csv2df.reader import Reader, open_csv
from csv2df.parcer import extract_tables
from csv2df.emitter import Emitter
from csv2df.validator import Validator


__all__ = ['get_dataframes', 'Vintage', 'Collection']


def get_dataframes(csvfile, spec=SPEC):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Args:
       csvfile (file connection or StringIO) - CSV file for parsing
       spec (spec.Specification) - pasing instructions, defaults to spec.SPEC
    
    Returns:  
       Three pandas dataframes at annual, qtr and monthly frequencies.  
    """
    tables = [t for csv_segment, pdef in Reader(csvfile, spec).items() 
                for t in extract_tables(csv_segment, pdef)]
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq='a')
    dfq = emitter.get_dataframe(freq='q')
    dfm = emitter.get_dataframe(freq='m')
    return dfa, dfq, dfm


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year=False, month=False):
        _year, _month = DateHelper.filter_date(year, month)
        self.year, self.month = _year, _month
        csv_path = PathHelper.locate_csv(_year, _month)
        with open_csv(csv_path) as csvfile:
            self.dfa, self.dfq, self.dfm = get_dataframes(csvfile)

    def dfs(self):
        """Shorthand for obtaining three dataframes."""
        return self.dfa, self.dfq, self.dfm

    def save(self):
        folder_path = PathHelper.get_processed_folder(self.year, self.month)
        self.dfa.to_csv(folder_path / 'dfa.csv')
        self.dfq.to_csv(folder_path / 'dfq.csv')
        self.dfm.to_csv(folder_path / 'dfm.csv')
        print("Saved dataframes to", folder_path)

    def validate(self):
        checker = Validator(self.dfa, self.dfq, self.dfm)
        checker.run()
        print("Test values parsed OK for", self)

    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)


class Collection:
    """Methods to manipulate entire set of data releases."""

    all_dates = DateHelper.get_supported_dates()

    @staticmethod
    def save_latest():
        vintage = Vintage(year=None, month=None)
        vintage.save()

    @staticmethod
    def approve_latest():
        """Quick check for algorithm on latest available data."""
        vintage = Vintage(year=None, month=None)
        vintage.validate()

    @staticmethod
    def save_all():
        for (year, month) in Collection.all_dates:
            Vintage(year, month).save()

    @staticmethod
    def approve_all():
        """Checks all dates, runs for about 1-2 min of a fast computer.
           May fail if dataset not complete, eg word2csv written only part
           of CSV file.
        """
        for year, month in Collection.all_dates:
            print("Checking", year, month)
            vintage = Vintage(year, month)
            vintage.validate()


if __name__ == "__main__":
    # Collection calls
    Collection.approve_latest()
    # Collection.approve_all()
    # Collection.save_latest()
    # Collection.save_all()

    # sample Vintage call
    year, month = 2017, 5
    vint = Vintage(year, month)
    vint.validate()
    dfa, dfq, dfm = vint.dfs()
