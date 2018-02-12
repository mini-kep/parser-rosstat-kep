"""Extract dataframes by year and month."""

from kep import FREQUENCIES, PARSING_DEFINITION
from kep.csv2df.dataframe_maker import Datapoints
from kep.df2xl.to_excel import save_xls
from kep.helper.date import Date
from kep.helper.path import InterimCSV, ProcessedCSV
from kep.validation.checkpoints import CHECKPOINTS, validate


class Vintage:
    """Represents dataset release for a given year and month.
        Performs interim CSV file parsing on construction and obtains 
        resulting dataframes.
    """
    def __init__(self, year: int, month: int, parsing_definition=PARSING_DEFINITION):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        parsing_definition.attach_data(csv_text)
        self.emitter = Datapoints(parsing_definition.tables)
        self.dfs = {freq: self.emitter.get_dataframe(freq) for freq in FREQUENCIES}

    @property
    def datapoints(self):        
        return self.emitter.datapoints

    def save(self, folder=None):
        csv_processed = ProcessedCSV(self.year, self.month, folder)
        for freq, df in self.dfs.items():
            path = csv_processed.path(freq)
            df.to_csv(path)
            print("Saved dataframe to", path)

    def validate(self):
        for freq in FREQUENCIES:
            df = self.dfs[freq]
            checkpoints = CHECKPOINTS[freq]

            try:
                validate(df, checkpoints)
            except ValueError as err:
                raise ValueError(f"Validated frequency: '{freq}'") from err

        print("Test values parsed OK for", self)

    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)


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
        #        (a) date format   
        #        (b) extra keys in dictionary
        #        (c) may be part of 
        Uploader(self.datapoints).post()

    def save(self, folder=None):
        ProcessedCSV(self.year, self.month).to_latest()

    def to_excel(self):
        save_xls()


if __name__ == "__main__": # pragma: no cover
    v = Vintage(2016, 10)
    v.validate()
    # Expected:
    # Test values parsed OK for Vintage(2016, 10)
