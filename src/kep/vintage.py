"""Get pandas dataframes for a given data and month.

*get_dataframes(path, parsing_definitions)*

*Vintage* class addresses dataset by year and month:

    Vintage(year, month).save()
    Vintage(year, month).validate()

*Collection* manipulates all datasets, released at various dates:

    Collection.save_all()
    Collection.approve_all()
"""
from kep.config import ProcessedCSV, SUPPORTED_DATES
from kep.checkpoints import CHECKPOINTS
from kep.extractor import Frame, isin

FREQUENCIES = ['a', 'q', 'm']


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year, month):
        self.year, self.month = year, month
        self.dfs = Frame(year, month).dfs

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