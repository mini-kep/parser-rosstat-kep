"""Get pandas dataframes for a given data and month.

*get_dataframes(csvfile, spec=SPEC)* is a function to get dataframes
    from *csvfile* connection under *spec* parsing instruction.

*Vintage* class addresses dataset by year and month:

    Vintage(year, month).save()
    Vintage(year, month).validate()

*Collection* manipulates all datasets, released at various dates:

    Collection.save_all()
    Collection.save_latest()
    Collection.approve_latest()
    Collection.approve_all()
"""
import pandas as pd

from config import PathHelper
from config import DateHelper
from csv2df.specification import SPEC
from csv2df.reader import Reader, open_csv
from csv2df.parser import extract_tables
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

    def __init__(self, year, month, helper=PathHelper):
        self.year, self.month = year, month
        self.folder_path = helper.get_processed_folder(year, month)
        csv_path = helper.locate_csv(year, month)
        with open_csv(csv_path) as csvfile:
            self.dfa, self.dfq, self.dfm = get_dataframes(csvfile)

    def dfs(self):
        """Shorthand for obtaining three dataframes."""
        return self.dfa, self.dfq, self.dfm

    def save(self):
        self.dfa.to_csv(self.folder_path / 'dfa.csv')
        self.dfq.to_csv(self.folder_path / 'dfq.csv')
        self.dfm.to_csv(self.folder_path / 'dfm.csv')
        print("Saved dataframes to", self.folder_path)
        return True

    def validate(self):
        checker = Validator(self.dfa, self.dfq, self.dfm)
        checker.run()
        print("Test values parsed OK for", self)
        return True

    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)


class Collection:
    """Methods to manipulate entire set of data releases."""

    all_dates = DateHelper.get_supported_dates()
    year, month = DateHelper.get_latest_date()
    latest_vintage = Vintage(year, month)

    @classmethod
    def save_latest(cls):
        cls.latest_vintage.save()

    @classmethod
    def approve_latest(cls):
        """Quick check for algorithm on latest available data."""
        cls.latest_vintage.validate()

    @classmethod
    def save_all(cls):
        for year, month in cls.all_dates:
            Vintage(year, month).save()

    @classmethod
    def approve_all(cls):
        """Checks all dates, runs for about 1-2 min of a fast computer.
           May fail if dataset not complete, eg word2csv written only part
           of CSV file.
        """
        for year, month in cls.all_dates:
            print("Checking", year, month)
            vintage = Vintage(year, month)
            vintage.validate()


if __name__ == "__main__":
    # Collection calls
    Collection.approve_latest()
    # Collection.approve_all()
    Collection.save_latest()
    # Collection.save_all()

    # sample Vintage call
    year, month = 2015, 5
    vint = Vintage(year, month)
    vint.validate()
    dfa, dfq, dfm = vint.dfs()
