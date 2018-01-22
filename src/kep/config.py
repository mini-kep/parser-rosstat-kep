"""Path and date helpers.

Constants:
    XL_PATH 
    UNPACK_RAR_EXE

Classes:
    DataFolder
    InterimCSV
    ProcessedCSV  
    
"""

from pathlib import Path
import pandas as pd


FREQUENCIES = ['a', 'q', 'm']


def find_repo_root():
    """Returns root folder for repository.
    Current file is assumed to be at:
        <repo_root>/src/kep/config.py
    """
    levels_up = 2
    return Path(__file__).parents[levels_up]



class Folders:
    root = find_repo_root()
    data = root / 'data'
    raw = data / 'raw'
    interim =  data / 'interim'
    processed = data / 'processed'
    latest = processed / latest


UNPACK_RAR_EXE = str(Folders.root / 'bin' / 'UnRAR.exe')
XL_PATH = str(Folders.root / 'output' / 'kep.xlsx')


def supported_dates():
    """Get a list of (year, month) tuples starting from (2009, 4)
       up to a previous recent month.

       Excludes (2013, 11) - no archive for this month.

    Returns:
        List of (year, month) tuples
    """
    start_date = '2009-04'
    end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
    dates = pd.date_range(start_date, end_date, freq='MS')
    excluded = (2013, 11)
    return [(date.year, date.month)
            for date in dates
            if (date.year, date.month) != excluded]


SUPPORTED_DATES = supported_dates()

def is_supported_date(year, month):
     if (year, month) not in SUPPORTED_DATES:
         raise ValueError(f'<{year}, {month}> is not a supported date.')
     else:
         return True
    

def md(folder):
    """Create *folder* if not exists"""
    if not folder.exists():
        folder.mkdir(parents=True)


class DataFolder:
    def __init__(self, year: int, month: int):
        if is_supported_date(year, month):
            self.year, self.month = year, month

    def year_month_folder(self, subfolder):
        year = str(self.year) 
        month = str(self.month).zfill(2)
        folder = subfolder / year / month
        md(folder)
        return folder 

    @property
    def raw(self):
        return self.year_month_folder(Folders.raw)

    @property
    def interim(self):
        return self.year_month_folder(Folders.interim)

    @property
    def processed(self):
        return self.year_month_folder(Folders.processed)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.year, self.month)

class LocalRarFile:
    def __init__(self, year: int, month: int):        
        self.folder = DataFolder(year, month).raw
        self.path = str(self.folder / 'ind.rar') 


class FileBase:
    # to override 
    path = Path()
    
    def exists(self):
        return self.path.exists()
    
    def text(self):
        return self.path.read_text(encoding='utf-8')

    def __len__(self):
        return self.path.stat().st_size


class InterimCSV(FileBase):
    def __init__(self, year: int, month: int):        
        self.path = DataFolder(year, month).interim / 'tab.csv'


class ProcessedCSV:
    def __init__(self, year: int, month: int):        
        self.folder = DataFolder(year, month).processed

    @staticmethod
    def make_filename(freq):
        return 'df{}.csv'.format(freq)

    def path(self, freq):
        return self.folder / self.make_filename(freq)


class Latest:

    md(DataFolder.latest)

    url = ('https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/'
           'master/data/processed/latest')

    def csv(freq):
        return DataFolder.latest / ProcessedCSV.make_filename(freq)





def get_latest_date(base_dir):
    """Return (year, month) tuple corresponding to
       latest filled subfolder of *base_dir*.
    """
    def max_subdir(folder):
        subfolders = [f.name for f in folder.iterdir() if f.is_dir()]
        return max(map(int, subfolders))
    year = max_subdir(base_dir)
    month = max_subdir(base_dir / str(year))
    return year, month


# latest date found in interm data folder
LATEST_DATE = get_latest_date(DataFolder._interim)
