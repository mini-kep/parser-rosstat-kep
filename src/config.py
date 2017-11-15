"""Path and date helpers:

   - :class:`PathHelper` and :func:`find_repo_root` to navigate repo filesystem
   - :class:`DateHelper` to manage release dates as (year, month)

"""

from pathlib import Path
import pandas as pd

__all__ = ['find_repo_root', 'PathHelper', 'DateHelper']


class WebSource(object):
    BASE_URL = 'https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/master/data/processed/latest'


INTERIM_CSV_FILENAME = 'tab.csv'
XL_FILENAME = 'kep.xlsx'


def md(folder):
    """Create *folder* if not exists"""
    if not folder.exists():
        folder.mkdir()


def is_found(filepath):
    """Raise error if file does not exist or 0 length."""
    if not filepath.exists():
        raise FileNotFoundError(filepath)
    elif filepath.stat().st_size == 0:
        raise FileNotFoundError('File has zero length: {}'.format(filepath))


def find_repo_root():
    """Returns root folder for repository.

    Current file is assumed to be at:
        <repo_root>/src/config.py

    """
    levels_up = 1
    return Path(__file__).parents[levels_up]


class DataFolder:
    data_root = find_repo_root() / 'data'
    _raw = data_root  / 'raw'
    _interim = data_root  / 'interim'
    _processed = data_root  / 'processed'
    _latest = _processed / 'latest'

    def __init__(self, year=None, month=None):
        DateHelper.validate(year, month)
        self.year, self.month = year, month
        self.guarantee_folders()
        
        
    def guarantee_folders(self):
        for base in [self._raw, self._interim, self._processed]:
            md(base)
            md(base / str(self.year))
            md(self.dated_folder(base)) 
        md(self._latest)    

  
    def dated_folder(self, which_subfolder):
        return which_subfolder / str(self.year) / str(self.month).zfill(2)
    
    @property
    def raw(self):
        return self.dated_folder(self._raw)

    @property
    def interim(self):
        return self.dated_folder(self._interim)

    @property
    def processed(self):
        return self.dated_folder(self._processed)

    def __repr__(self):
        return "DataFolder({}, {})".format(self.year, self.month)


class LocalCSV(DataFolder):
    
    @property
    def interim(self, filename=INTERIM_CSV_FILENAME):
        return super().interim / filename

    def processed(self, freq):
        return super().processed / 'df{}.csv'.format(freq)

    def latest(self, freq):
        return super()._latest / 'df{}.csv'.format(freq)

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

LATEST = get_latest_date(DataFolder._interim) 



class PathHelper:
    """
    In parsing used by:

     - :class:`download.download.RemoteFile`
     - :func:`word2csv.word.make_interim_csv`
     - :class:`csv2df.runner.Vintage`

    """

    # folders

    #def get_raw_folder(year, month):
    #    return DataFolder(year, month).raw

    def get_processed_folder(year, month):
        """Return processed CSV file folder based on *year* and *month*.

           The processed CSV file folder is used to write <df*.csv> files.

           Returns:
               pathlib.Path() instance.
        """
        return DataFolder(year, month).get_processed_folder()

    def get_latest_folder():
        return DataFolder.latest

    # files

    def locate_csv(year: int, month: int):
        """Return interim CSV file based on *year* and *month*.

           Returns:
                pathlib.Path() instance
        """
        return DataFolder(year, month).get_interim_csv()

    def get_csv_in_latest_folder(freq):
        return DataFolder.latest / 'df{}.csv'.format(freq)

    def get_xl_path(filename=XL_FILENAME):
        return str(find_repo_root() / 'output' / filename)

    # bin file
    def get_unrar_binary():
        root = find_repo_root()
        unrar_filename = "UnRAR.exe"
        return str(root / 'bin' / unrar_filename)


UNPACK_RAR_EXE = str(find_repo_root() / 'bin' / 'UnRAR.exe') 


class DateHelper:
    def get_latest_date():
        """Return year and month for latest available interim data folder.

        Returns:
            (year, month) tuple of two integers.

        """
        return DataFolder.get_latest_date()

    def validate(year, month):
        if (year, month) not in DateHelper.get_supported_dates():
            raise ValueError(f'Not in supported date range: {year}, {month}')

    def get_supported_dates():
        return supported_dates()


def supported_dates():
    """Get a list of (year, month) tuples starting from (2009, 4)
       up to month before current.

       For example, on September 1 will return (8, 2017).

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


