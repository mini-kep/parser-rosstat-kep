"""Extract dataframes by year and month."""

from kep import FREQUENCIES
from kep.csv2df.specification import PARSING_SPECIFICATION
from kep.csv2df.dataframe_maker import create_dataframe
from kep.df2xl.to_excel import save_xls
from kep.helper.date import Date
from kep.helper.path import InterimCSV, ProcessedCSV
from kep.validation.checkpoints import (
    CHECKPOINTS,
    OPTIONAL_CHECKPOINTS,
    validate2
)


class Vintage:
    """Represents dataset release for a given year and month.
    
       Parses interim CSV file and obtains resulting dataframes.
    """
    def __init__(self, year: int, month: int, parsing_spec=PARSING_SPECIFICATION):
        self.year, self.month = year, month
        csv_text = InterimCSV(year, month).text()
        parsing_spec.attach_data(csv_text)
        self.values = parsing_spec.values 
        self.dfs = {freq: create_dataframe(self.values, freq) for freq in FREQUENCIES}

    @property
    def datapoints(self):        
        return self.emitter.datapoints

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
    # Expected output:
    # Test values parsed OK for Vintage(2016, 10)

#    import pandas as pd
#    # TODO: convert to test for to_csv(), hitting deaccumulation procedure
#    assert pd.DataFrame([{'a': 1}]).to_csv(float_format='%.2f') == ',a\n0,1\n'
#    assert pd.DataFrame([{'a': 1.0005}]).to_csv(float_format='%.2f') == ',a\n0,1.00\n'
#    
#    ix = list(reversed(Date.supported_dates))[1:]
#    for date in ix:
#        Vintage(*date).validate()
   
    # FIXME: first fail here

#     Test values parsed OK for Vintage(2010, 2)
# Traceback (most recent call last):
#
#   File "<ipython-input-50-45ec4d698994>", line 1, in <module>
#     runfile('C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/kep/vintage.py', wdir='C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/kep')
#
#   File "D:\Continuum\Anaconda3\lib\site-packages\spyder\utils\site\sitecustomize.py", line 880, in runfile
#     execfile(filename, namespace)
#
#   File "D:\Continuum\Anaconda3\lib\site-packages\spyder\utils\site\sitecustomize.py", line 102, in execfile
#     exec(compile(f.read(), filename, 'exec'), namespace)
#
#   File "C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/kep/vintage.py", line 95, in <module>
#     Vintage(*date).validate()
#
#   File "C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/kep/vintage.py", line 49, in validate
#     strict=False)
#
#   File "C:\Users\PogrebnyakEV\Desktop\mini-kep\kep\src\kep\validation\checkpoints.py", line 308, in validate2
#     echo(msg, True)
#
#   File "C:\Users\PogrebnyakEV\Desktop\mini-kep\kep\src\kep\validation\checkpoints.py", line 297, in echo
#     raise ValidationError(msg)
#
# ValidationError: Required checkpoints not found in dataframe: {Checkpoint(date='1999', freq='a', name='AGROPROD_yoy', value=103.8)}
