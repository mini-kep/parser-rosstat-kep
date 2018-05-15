"""Extract dataframes by year and month."""

from kep import FREQUENCIES

from kep.parsing_definition import PARSING_DEFINITIONS
from kep.csv2df.allocation import yield_parsing_assingments
from kep.csv2df.parser import evaluate_assignment

from kep.csv2df.dataframe_maker import create_dataframe
from kep.df2xl.to_excel import save_xls
from kep.helper.date import Date
from kep.helper.path import InterimCSV, ProcessedCSV
from kep.validation.checkpoints import (
    CHECKPOINTS,
    OPTIONAL_CHECKPOINTS,
    validate2
)

def get_values(csv_text, pdefs=PARSING_DEFINITIONS): 
    jobs_list = list(yield_parsing_assingments(pdefs, csv_text))
    return [v for a in jobs_list for v in evaluate_assignment(a)]


class Vintage:
    """Represents dataset release for a given year and month.
    
       Parses interim CSV file and obtains resulting dataframes.
    """
    def __init__(self, year: int, month: int):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        self.values = get_values(csv_text)
        self.dfs = {freq: create_dataframe(self.values, freq) for freq in FREQUENCIES}

    def save(self, folder=None):
        csv_processed = ProcessedCSV(self.year, self.month, folder)
        for freq, df in self.dfs.items():
            path = csv_processed.path(freq)
            # Convert 1524.3999999999996 back to 1524.4
            # Deaccumulation procedure in parser.py responsible  
            # for float number generation. 
            # WONTFIX: the risk is loss of data for exchange rate, 
            #          may need fomatter by column. annual values can be
            #          a guidance for a number of decimal positions.
            df.to_csv(path, float_format='%.2f')
            print("Saved dataframe to", path)

    def validate(self):
        for freq in FREQUENCIES:
            validate2(df=self.dfs[freq],
                      required_checkpoints=CHECKPOINTS[freq],
                      additional_checkpoints=OPTIONAL_CHECKPOINTS[freq],
                      strict=False)
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
        #           (a) date format   
        #           (b) extra keys in dictionary
        Uploader(self.datapoints).post()

    def save(self, folder=None):
        ProcessedCSV(self.year, self.month).to_latest()

    def to_excel(self):
        save_xls()


if __name__ == "__main__": # pragma: no cover
    v = Vintage(2018, 1)
    v.validate()
    v.save()
