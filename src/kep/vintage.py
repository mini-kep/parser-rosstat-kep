"""Extract dataframes by year and month."""

from kep import FREQUENCIES, PARSING_DEFINITION
from kep.parsing_definition.checkpoints import CHECKPOINTS, validate
from kep.helper.path import InterimCSV, ProcessedCSV
from kep.csv2df.dataframe_maker import Datapoints

class Vintage:
    """Represents dataset release for a given year and month.
    Performs interim CSV file parsing on init.*
    """

    def __init__(
            self,
            year: int,
            month: int,
            parsing_definition=PARSING_DEFINITION):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        parsing_definition.attach_data(csv_text)
        emitter = Datapoints(parsing_definition.tables)
        self.dfs = {freq: emitter.get_dataframe(freq) for freq in FREQUENCIES}

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
            validate(df, checkpoints)
        print("Test values parsed OK for", self)

    def upload(self, password):
        # TODO: upload to database
        raise NotImplementedError

    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)


if __name__ == "__main__": # pragma: no cover
    v = Vintage(2016, 10)
    v.validate()
    # Test values parsed OK for Vintage(2016, 10)
