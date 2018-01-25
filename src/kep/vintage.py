"""Get pandas dataframes for a given data and month from a processed CSV file.

*Vintage* class addresses dataset for a given month:

    Vintage(year, month).save()
    Vintage(year, month).validate()

*Collection* manipulates datasets for all available months:

    Collection.save_all()
    Collection.approve_all()

"""

from kep.config import FREQUENCIES, InterimCSV, ProcessedCSV, SUPPORTED_DATES
from kep.csv2df.emitter import Emitter
from kep.definitions.definitions import DEFINITION
from kep.checkpoints import CHECKPOINTS


def is_found(df, d):
    dt = d['date']
    colname = d['name']
    x = d['value']
    try:
        return df.loc[dt, colname].iloc[0] == x
    except KeyError:
        return False

def is_valid(df, checkpoints):
    flags = [is_found(df, c) for c in checkpoints]
    if not all(flags):
        missed_points = [c for f, c in zip(flags, checkpoints) if not f]
        raise ValueError(missed_points)
    return True    

def extract_frames(csv_text, parsing_definition):
    csv_text = InterimCSV(year, month).text()
    parsing_definition = parsing_definition.attach_data(csv_text)
    emitter = Emitter(parsing_definition.tables)
    return {freq: emitter.get_dataframe(freq) for freq in FREQUENCIES}

def emitter(year, month, parsing_definition=DEFINITION):
    csv_text = InterimCSV(year, month).text()
    parsing_definition = parsing_definition.attach_data(csv_text)
    return Emitter(parsing_definition.tables)    


class Vintage:
    """Represents dataset release for a given year and month."""
    def __init__(self, year: int, month: int, parsing_definition=DEFINITION):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        self.dfs = extract_frames(csv_text, parsing_definition)

    def save(self):
        csv_processed = ProcessedCSV(self.year, self.month)
        for freq, df in self.dfs.items():
            path = csv_processed.path(freq)
            df.to_csv(path)
            print("Saved dataframe to", path)

    def validate(self):
        for freq in FREQUENCIES:
            df = self.dfs[freq]
            checkpoints = CHECKPOINTS[freq]
            flags = [is_found(df, c) for c in checkpoints]
            if not all(flags):
                missed_points = [c for f, c in zip(
                    flags, checkpoints) if not f]
                raise ValueError(missed_points)
        print("Test values parsed OK for", self)

    def upload(self, password):
        # TODO: upload to databse
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
