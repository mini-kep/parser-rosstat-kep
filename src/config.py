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


def md(folder, i=0):
    """Create *folder* if not exists. Also create up to 3 parent folders."""
    if i > 3:
        msg = "Cannot create full path, iteration too deep: {}".format(folder)
        ValueError(msg)
    if not folder.exists():
        parent = folder.parent
        if not parent.exists():
            i += 1
            md(parent, i)
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
    root = Path(__file__).parents[levels_up]
    assert root.name == 'mini-kep'
    return root


class DataFolder:
    root = find_repo_root()
    raw = root / 'data' / 'raw'
    interim = root / 'data' / 'interim'
    processed = root / 'data' / 'processed'
    latest = root / 'data' / 'processed' / 'latest'

    def __init__(self, year=None, month=None):
        DateHelper.validate(year, month)
        self.year, self.month = year, month
        # TODO: instantinating folders here is risky
        # self.make_dirs()

    @classmethod
    def get_latest_date(cls):
        """Return (year, month) tuple corresponding to latest filled
           *data/interim* subfolder."""

        def max_subdir(folder):
            subfolders = [f.name for f in folder.iterdir() if f.is_dir()]
            return max(map(int, subfolders))

        root = cls.interim
        year = max_subdir(root)
        month = max_subdir(root / str(year))
        return year, month

    def make_dirs(self):
        for folder in [self.get_raw_folder(),
                       self.get_interim_folder(),
                       self.get_processed_folder()]:
            md(folder)

    def _local_folder(self, parent_folder):
        folder = parent_folder / str(self.year) / str(self.month).zfill(2)
        # WARNING: risky - may get to here from tests
        md(folder)
        return folder

    def get_raw_folder(self):
        return self._local_folder(self.raw)

    def get_interim_folder(self):
        return self._local_folder(self.interim)

    def get_processed_folder(self):
        return self._local_folder(self.processed)

    def get_interim_csv(self, filename=INTERIM_CSV_FILENAME):
        return self.get_interim_folder() / filename

    def __repr__(self):
        return "DataFolder({}, {})".format(self.year, self.month)


class PathHelper:
    """
    In parsing used by:
       
     - :class:`download.download.RemoteFile`
     - :func:`word2csv.word.make_interim_csv`
     - :class:`csv2df.runner.Vintage`
     
    """


    # folders

    def get_raw_folder(year, month):
        return DataFolder(year, month).get_raw_folder()

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
        """Get a list of (year, month) tuples starting from (2009, 4)
           up to month before current.

           For example, on September 1 will return (8, 2017).

           Excludes (2013, 11) - no archive for this month.

        Returns:
            List of (year, month) tuples
        """
        start_date = '2009-4'
        end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
        dates = pd.date_range(start_date, end_date, freq='MS')
        excluded = (2013, 11)
        return [(date.year, date.month) for date in dates
                if (date.year, date.month) != excluded]
