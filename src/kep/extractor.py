"""Extract dataframes."""

from kep.config import FREQUENCIES, InterimCSV, ProcessedCSV
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

class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year: int, month: int, parsing_definition=DEFINITION):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        parsing_definition.attach_data(csv_text)
        emitter = Emitter(parsing_definition.tables)
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
            flags = [is_found(df, c) for c in checkpoints]
            if not all(flags):
                missed_points = [c for f, c in zip(flags, checkpoints) if not f]
                raise ValueError(missed_points)
        print("Test values parsed OK for", self)
    
    def upload(self, password):
        # TODO: upload to databse
        pass
    
    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)
