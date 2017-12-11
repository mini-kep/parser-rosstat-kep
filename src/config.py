"""Path and date helpers."""

from pathlib import Path
import pandas as pd

__all__ = ['find_repo_root', 'DataFolder', 'InterimCSV', 'ProcessedCSV']


FREQUENCIES = ['a', 'q', 'm']

def find_repo_root():
    """Returns root folder for repository.
    Current file is assumed to be at:
        <repo_root>/src/config.py
    """
    levels_up = 1
    return Path(__file__).parents[levels_up]


UNPACK_RAR_EXE = str(find_repo_root() / 'bin' / 'UnRAR.exe') 
XL_PATH = str(find_repo_root() / 'output' / 'kep.xlsx')


def supported_dates():
    """Get a list of (year, month) tuples starting from (2009, 4)
       up to month before current.
       
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


def md(folder):
    """Create *folder* if not exists"""
    if not folder.exists():
        folder.mkdir()


class DataFolder:
    data_root = find_repo_root() / 'data'
    _raw = data_root  / 'raw'
    _interim = data_root  / 'interim'
    _processed = data_root  / 'processed'
    latest = _processed / 'latest'
    
    def __init__(self, year=None, month=None):
        if (year, month) not in SUPPORTED_DATES:
            raise ValueError(f'<{year}, {month}> is not a supported date.')
        self.year, self.month = year, month
        self.guarantee_folders()        
        
    def guarantee_folders(self):
        for base in [self._raw, self._interim, self._processed]:
            md(base)
            md(base / str(self.year))
            md(self.year_month_folder(base))             
  
    def year_month_folder(self, which_subfolder):
        return which_subfolder / str(self.year) / str(self.month).zfill(2)
    
    @property
    def raw(self):
        return self.year_month_folder(self._raw)

    @property
    def interim(self):
        return self.year_month_folder(self._interim)

    @property
    def processed(self):
        return self.year_month_folder(self._processed)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.year, self.month)


class File(DataFolder):

    @property
    def path(self):
        self.data_root

    def exists(self):
        return self.path.exists()
    
    def __len__(self):
        return self.path.stat().st_size


class InterimCSV(File):
    
    @property
    def path(self):
        return super().interim / 'tab.csv'
        

class ProcessedCSV(File):
    
    @staticmethod
    def make_filename(freq):
        return 'df{}.csv'.format(freq)

    def path(self, freq):
        return super().processed / self.make_filename(freq)


class Latest:
    
    md(DataFolder.latest)
    
    url = ('https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/'
           'master/data/processed/latest')       
    
    def csv(freq):
        return DataFolder.latest / ProcessedCSV.make_filename(freq)
    
    
class LocalRarFile(DataFolder):
    @property
    def path(self):
        return str(self.raw / 'ind.rar')    

    @property
    def folder(self):
        return str(Path(self.path).parent)


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
