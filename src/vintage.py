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

from config import InterimCSV, ProcessedCSV, SUPPORTED_DATES
from csv2df.specification import PARSING_DEFINITION
from csv2df.reader import get_segment_with_pdef
from csv2df.parser import extract_tables
from csv2df.emitter import Emitter
from validator import validate


__all__ = ['get_dataframes', 'Vintage', 'Collection']

FREQUENCIES = ['a', 'q', 'm']


def get_dataframes(path, spec=PARSING_DEFINITION):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Args:
       csvfile (file connection or StringIO) - CSV file for parsing
       spec (spec.Specification) - pasing instructions, defaults to spec.SPEC

    Returns:
       Three pandas dataframes at annual, qtr and monthly frequencies
       in a dictionary.
    """
    jobs = get_segment_with_pdef(path, spec['default'], spec['segments'])
    tables = [t for csv_segment, pdef in jobs
                for t in extract_tables(csv_segment, pdef)]
    emitter = Emitter(tables)
    return {freq: emitter.get_dataframe(freq) for freq in FREQUENCIES}


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year, month):
        self.year, self.month = year, month
        csv_interim = InterimCSV(year, month)
        self.dfs = get_dataframes(csv_interim.path)

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
    year, month = 2015, 5
    vint = Vintage(year, month)
    vint.validate()
    dfa, dfq, dfm = [vint.dfs[freq] for freq in 'aqm']