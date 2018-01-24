"""Path and date helpers.

Constants:
    FREQUENCIES
    SUPPORTED_DATES

Paths as strings:   
    UNPACK_RAR_EXE
    XL_PATH

Classes:
    DataFolder
    InterimCSV
    ProcessedCSV
    LocalRarFile
"""

from pathlib import Path

import pandas as pd

FREQUENCIES = ['a', 'q', 'm']

def supported_dates(start_date = '2009-04', exclude_dates = ['2013-11']):
    """Get a list of (year, month) tuples starting from (2009, 4)
       up to a previous recent month.

       Excludes (2013, 11) - no archive for this month.

    Returns:
        List of (year, month) tuples.
    """
    end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
    dates = pd.date_range(start_date, end_date, freq='MS')
    exclude = map(pd.to_datetime, exclude_dates)
    return [(date.year, date.month) for date in dates.drop(exclude)]


SUPPORTED_DATES = supported_dates()


def is_supported_date(year, month):
    if (year, month) in SUPPORTED_DATES:
        return True
    else:
        raise ValueError(f'<{year}, {month}> is not a supported date.') 


def md(folder):
    """Create *folder* if not exists.
       Also creates parent folders.
    """
    if not folder.exists():
        folder.mkdir(parents=True)


def find_repo_root():
    """Returns root folder for repository.
    Current file is assumed to be at:
        <repo_root>/src/kep/config.py
    """
    levels_up = 2
    return Path(__file__).parents[levels_up]


class Folders:
    """Folder system for the data in project:

        <repo root>
            /data
                /raw
                /interim
                /processed
                    /latest

        Folder structure follows Data Science Cookiecutter template.
    """
    root = find_repo_root()
    _data = root / 'data'
    raw = _data / 'raw'
    interim = _data / 'interim'
    processed = _data / 'processed'
    latest = processed / 'latest'
    md(latest)


UNPACK_RAR_EXE = str(Folders.root / 'bin' / 'UnRAR.exe')
XL_PATH = str(Folders.root / 'output' / 'kep.xlsx')


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
    """Prototype for file handler classes. Has file properties."""
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
        if freq in FREQUENCIES:
            return 'df{}.csv'.format(freq)
        else:
            raise ValueError(freq)

    def path(self, freq: str):
        return self.folder / self.make_filename(freq)

if __name__ == "__main__":
    pass