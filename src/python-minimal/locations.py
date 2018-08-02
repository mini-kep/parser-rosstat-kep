"""Dates for the project."""

import pandas as pd

def supported_dates(start_date='2009-04', exclude_dates=['2013-11']):
    """Get a list of (year, month) tuples starting from (2009, 4) up to
       a previous recent month. This a 'supported date list'.
       Excludes (2013, 11) - no archive for this month.
    Returns:
        List of (year: int, month: int) tuples.
    """
    end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
    dates = pd.date_range(start_date, end_date, freq='MS')
    exclude = map(pd.to_datetime, exclude_dates)
    return [(date.year, date.month) for date in dates.drop(exclude)]



def date_span(start_date, end_date):
    supported_date_list =  supported_dates()
    return [(date.year, date.month) for date in 
             pd.date_range(start_date, end_date, freq='MS')
             if (date.year, date.month) in supported_date_list]  
    


def is_latest(year: int, month: int):
    return (year, month) in supported_dates()[:-2]

#"""Run full cycle of data processing from download to saving dataframe."""
#
from pathlib import Path
#import shutil
#from io import StringIO
#
#import pandas as pd
#
#
#from inputs import UNITS, YAML_DOC, verify
#from dispatch import evaluate
#from util.remote import Downloader, Unpacker
#from util.word import folder_to_csv
## WONTFIX: maybe this is not as uril, part of dataflow
#from util.dataframe import create_dataframe
#from util.date import is_latest, supported_dates
#from util.to_excel import save_excel
#
#
#FREQUENCIES = list('aqm')
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / 'data'
OUTPUT_ROOT = PROJECT_ROOT / 'output'

#assert DATA_ROOT.exists()
#assert OUTPUT_ROOT.exists()
#
#

def md(folder):
    if not folder.exists():
        folder.mkdir(parents=True)
    return folder
#
#
#class OutputLocations(object):
#    def __init__(self, output_root=OUTPUT_ROOT):
#        self.out = Path(output_root)
#        self.xlsx = str(self.out / 'kep.xlsx')
#
#


def as_string(func):
    def wrapper(*arg, **kwarg):
        return str(func(*arg, **kwarg))
    return wrapper
    

def inner_folder(data_root, tag, year, month):
    allowed_tags = ('raw', 'interim', 'processed')
    if tag in allowed_tags:            
        return data_root / tag / str(year) / str(month).zfill(2)
    else:
        raise ValueError(f'{tag} not supported, must be any of {allowed_tags}')

def latest_folder(data_root=DATA_ROOT):
    return data_root / 'processed' / 'latest'


@as_string
def parsing_instructions(data_root=DATA_ROOT):
    return data_root / 'instructions.txt'

@as_string
def unit_mapper(data_root=DATA_ROOT):
    return data_root / 'base_units.txt'

@as_string
def interim_csv(year: int, month: int, data_root=DATA_ROOT):
    return inner_folder(data_root, 'interim', year, month) / 'tab.csv'



    def processed_csv(self, freq: str):
        return str(self.inner_path('processed') / self.filename(freq))

    def latest_csv(self, freq: str):
        return str(self.inner_path('latest') / self.filename(freq))




class Location(object):
    def __init__(self, 
                 year: int,
                 month: int,
                 data_root=DATA_ROOT
                 ):
        if (year, month) not in supported_dates():
            raise ValueError(year, month)
        self.year = year
        self.month = month
        self.data = Path(data_root)

    @property
    def raw_folder(self):
        return self.inner_path('raw')

    @property
    def rar(self):
        return str(self.raw_folder / 'download.rar')

    def interim_csv(self):
        return str(self.inner_path('interim') / 'tab.csv')

    def processed_csv(self, freq: str):
        return str(self.inner_path('processed') / self.filename(freq))

    def latest_csv(self, freq: str):
        return str(self.inner_path('latest') / self.filename(freq))

    @staticmethod
    def filename(freq):
        return 'df{}.csv'.format(freq)


#def to_latest(year: int, month: int, loc):
#    """Copy csv files from folder like *processed/2017/04* to
#       *processed/latest*.
#    """
#    for freq in FREQUENCIES:
#        src = loc.processed_csv(freq)
#        dst = loc.latest_csv(freq)
#        shutil.copyfile(str(src), str(dst))
#        print("Updated", dst)
#    print(f"Latest folder now refers to {loc.year}-{loc.month}")
#
#
#def read_csv(source):
#    """Wrapper for pd.read_csv1(). Treats first column at time index.
#       Returns:
#           pd.DataFrame()
#    """
#    converter_arg = dict(converters={0: pd.to_datetime}, index_col=0)
#    return pd.read_csv(source, **converter_arg)
#
#
#def proxy(path):
#    """A workaround for pandas problem with non-ASCII paths on Windows
#       See <https://github.com/pandas-dev/pandas/issues/15086>
#       Args:
#           path (pathlib.Path) - CSV filepath
#       Returns:
#           io.StringIO with CSV content
#    """
#    content = Path(path).read_text()
#    return StringIO(content)
#
#
#def get_dataframe(year, month, freq):
#    """Read dataframe from local folder"""
#    loc = Locations(year, month, DATA_ROOT, OUTPUT_ROOT)
#    filelike = proxy(loc.processed_csv(freq))
#    return read_csv(filelike)
#
#
#def prepare_data(year, month,
#                 data_root=DATA_ROOT,
#                 force_download=False,
#                 force_unrar=False,
#                 force_convert_word=False):
#    # filesystem
#    loc = Locations(year, month, data_root)
#    INTERIM_FOUND = loc.interim_csv.exists()
#    # perisist data
#    if force_download or not INTERIM_FOUND:
#        d = Downloader(year, month, loc.archive_filepath)
#        d.run()
#        print(d.status)
#    if force_unrar or not INTERIM_FOUND:
#        u = Unpacker(loc.archive_filepath, loc.raw_folder)
#        u.run()
#        print(u.status)
#    # convert Word to csv
#    if force_convert_word or not INTERIM_FOUND:
#        folder_to_csv(loc.raw_folder, loc.interim_csv)
#
#
#def parse(year,
#          month,
#          units_dict=UNITS,
#          yaml_doc=YAML_DOC,
#          data_root=DATA_ROOT,
#          validator=verify):
#    # filesystem
#    loc = Locations(year, month, data_root)
#    # parse
#    text = loc.interim_csv.read_text(encoding='utf-8')
#    values = list(evaluate(text, units_dict, yaml_doc))
#    # save three dataframes
#    dfs = {}
#    for freq in 'aqm':
#        df = create_dataframe(values, freq)
#        dfs[freq] = df
#        validator(df, freq)
#        df.to_csv(str(loc.processed_csv(freq)))
#    return dfs
#
#
#def unpack(dfs):
#    return (dfs[freq] for freq in FREQUENCIES)
#
#
#def save(year, month, dfs, data_root=DATA_ROOT, output_root=OUTPUT_ROOT):
#    loc = Locations(year, month, data_root)
#    oloc = OutputLocations(output_root)
#    if is_latest(year, month):
#        to_latest(year, month, loc)
#        save_excel(oloc.xlsx, dfs)
#
#
#def all_months():
#    for year, month in reversed(supported_dates()[:-2]):
#        print("\n" * 5, year, month)
#        dfa, dfq, dfm = unpack(parse(year, month))
#
#
#if __name__ == '__main__':
#    # typical workflow
#    import sys
#    try:
#        year = int(sys.argv[1])
#        month = int(sys.argv[2])
#    except IndexError:
#        year, month = 2018, 4
#    prepare_data(year, month)
#    dfs = parse(year, month)
#    save(year, month, dfs)
#dfa, dfq, dfm = unpack(dfs)