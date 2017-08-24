"""Get dataframes for given data nad month.

*Vintage* class addresses dataset by year and month:

   Vintage(year, month).validate()
   Vintage(year, month).save()

*Collection* manipulates all datasets, released at various dates:

    - save_all()
    - save_latest()
    - approve_latest()
    - approve_all()

"""

import warnings

import kep2.helper as helper

from kep2.specification import SPEC
from kep2.reader import Reader, open_csv
from kep2.parcer import get_tables
from kep2.emitter import Emitter
from kep2.validator import Validator


# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)


def get_dataframes(csvfile, spec=SPEC):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Arg:
      csvfile (file connection or StringIO) - CSV file for parsing
      spec (spec.Specification) - pasing instructions, defaults to spec.SPEC
    """
    rdr = Reader(csvfile, spec)
    parsing_inputs = rdr.items()
    tables = get_tables(parsing_inputs)
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq='a')
    dfq = emitter.get_dataframe(freq='q')
    dfm = emitter.get_dataframe(freq='m')
    return dfa, dfq, dfm


class Vintage:
    """Represents dataset release for a given year and month."""

    @staticmethod
    def filter_date(year, month):
        """Set (year, month) to latest date if year or month omitted."""
        latest_year, latest_month = helper.get_latest_date()
        return year or latest_year, month or latest_month

    def __init__(self, year=False, month=False):
        self.year, self.month = self.filter_date(year, month)
        csv_path = helper.locate_csv(self.year, self.month)
        with open_csv(csv_path) as csvfile:
            self.dfa, self.dfq, self.dfm = get_dataframes(csvfile)

    def dfs(self):
        """Shorthand for obtaining three dataframes."""
        return self.dfa, self.dfq, self.dfm

    def save(self):
        folder_path = helper.get_processed_folder(self.year, self.month)
        self.dfa.to_csv(folder_path / 'dfa.csv')
        self.dfq.to_csv(folder_path / 'dfq.csv')
        self.dfm.to_csv(folder_path / 'dfm.csv')
        print("Saved dataframes to", folder_path)

    def validate(self):
        checker = Validator(self.dfa, self.dfq, self.dfm)
        checker.run()
        print("Test values parsed OK for", self)

    def __repr__(self):
        return "Vintage ({}, {})".format(self.year, self.month)


class Collection:
    """Methods to manipulate entire set of data releases."""

    @staticmethod
    def save_all():
        for (year, month) in helper.filled_dates():
            Vintage(year, month).save()

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
    def approve_all():
        """Checks all dates, runs for about 1-2 min of a fast computer.
           May fail if dataset not complete, eg word2csv written only part
           of CSV file.
        """
        for year, month in helper.filled_dates():
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
