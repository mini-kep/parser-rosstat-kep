"""Folder and file paths for the project.

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
import shutil

from kep import FREQUENCIES
from kep.helper.date import is_supported_date, is_latest_date


def md(folder):
    """Create *folder* if not exists.
       Also creates parent folders.
    """
    if not folder.exists():
        folder.mkdir(parents=True)


def find_repo_root():
    """Returns root folder for repository.
    Current file is assumed to be:
        <repo_root>/src/kep/helper/<this file>.py
    """
    levels_up = 3
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

# possible replacement for Folders class

class Folder:
    def __init__(self, root=None):
        if not root:
            root = find_repo_root()
        self.root = root
        data_folder = root / 'data'
        self.raw = data_folder / 'raw'
        self.interim = data_folder / 'interim'
        self.processed = data_folder / 'processed'
        self.latest = self.processed / 'latest'

# end ------------------------

ROOT = find_repo_root()
UNPACK_RAR_EXE = str(ROOT / 'bin' / 'UnRAR.exe')
XL_PATH = str(ROOT / 'output' / 'kep.xlsx')


class DataFolder:
    def __init__(self, year: int, month: int, root = ROOT):
        if is_supported_date(year, month):
            self.year, self.month = year, month
        data_folder = root / 'data'
        self.raw_folder = data_folder / 'raw'
        self.interim_folder = data_folder / 'interim'
        self.processed_folder = data_folder / 'processed' 
        self.latest_folder = self.processed_folder / 'latest' 

    def year_month_subfolder(self, subfolder):
        year = str(self.year)
        month = str(self.month).zfill(2)
        folder = subfolder / year / month
        md(folder)
        return folder

    @property
    def raw(self):
        return self.year_month_subfolder(self.raw_folder)

    @property
    def interim(self):
        return self.year_month_subfolder(self.interim_folder)

    @property
    def processed(self):
        return self.year_month_subfolder(self.processed_folder)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.year, self.month)


class LocalRarFile:
    def __init__(self, year: int, month: int):
        self.folder = DataFolder(year, month).raw
        self.path = str(self.folder / 'ind.rar')


class FileBase:
    """Prototype for file handler classes.
       Has file methods and properties.
    """
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
    """A family of three CSV files by frequency. 
       These files hold parsing result."""
    def __init__(self, year: int, month: int, root=ROOT):
        self.year, self.month = year, month
        self.folder_navigator = DataFolder(year, month, root)

    @staticmethod
    def make_filename(freq):
        if freq in FREQUENCIES:
            return 'df{}.csv'.format(freq)
        else:
            raise ValueError(freq)

    def path(self, freq: str):
        return self.folder_navigator.processed / self.make_filename(freq)

    def path_in_latest_folder(self, freq: str):   
        md(self.folder_navigator.latest)            
        return self.folder_navigator.latest / self.make_filename(freq) 

    def copy_to_latest(self, freq: str):
        """Copy csv files from folder like
               *processed/2017/04
           to
               *processed/latest folder.
        """  
        src = str(self.path(freq))
        dst = str(self.path_in_latest_folder(freq))
        shutil.copyfile(src, dst)
        print("Updated", dst)

    def to_latest(self):
        if is_latest_date(self.year, self.month) :
            for freq in FREQUENCIES:    
                self.copy_latest(freq)
        else:
            print(f"Date {self.year}, {self.month} cannot be copied to *latest* folder.")



# def get_path_in_latest_folder(freq: str):
#     return Folders.latest / ProcessedCSV.make_filename(freq)


# def copy_to_latest_folder(year: int, month: int):
#     """Copy csv files from folder like
#             *processed/2017/04
#         to
#            *processed/latest folder.
#     """
#     csv_file = ProcessedCSV(year, month)
#     for freq in FREQUENCIES:
#         src = str(csv_file.path(freq))
#         dst = str(get_path_in_latest_folder(freq))
#         shutil.copyfile(src, dst)
#         print("Updated", dst)


if __name__ == "__main__":
    pass
