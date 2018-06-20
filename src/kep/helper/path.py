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
from kep.helper.date import Date


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

ROOT = find_repo_root()
DATA_FOLDER = ROOT / 'data' 
UNPACK_RAR_EXE = str(ROOT / 'bin' / 'UnRAR.exe')
XL_PATH = str(ROOT / 'output' / 'kep.xlsx')
    

def latest_folder(data_root_folder=None):
    folder = DataFolderBase(data_root_folder).latest 
    md(folder)  
    return folder

class DataFolderBase:
    def __init__(self, data_folder=None):
        if not data_folder:
            data_folder = DATA_FOLDER 
        self.raw_folder = data_folder / 'raw'
        self.interim_folder = data_folder / 'interim'
        self.processed_folder = data_folder / 'processed' 
        self.latest = self.processed_folder / 'latest' 
    

class DataFolder(DataFolderBase):
    def __init__(self, year: int, month: int, data_folder = None):        
        super().__init__(data_folder)
        self.date = Date(year, month)

    def year_month_subfolder(self, subfolder):        
        year = str(self.date.year)
        month = str(self.date.month).zfill(2)
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
                                   self.date.year, self.date.month)


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


class LatestCSV:
     def __init__(self, data_root_folder=None):
        self.folder = latest_folder(data_root_folder)
        
     def path(self, freq: str):             
        return self.folder / ProcessedCSV.make_filename(freq) 

class ProcessedCSV:
    """A family of three CSV files by frequency. 
       The files hold parsing result."""
       
    def __init__(self, year: int, month: int, data_root_folder=None):
        self.date = Date(year, month)
        self.folder = DataFolder(year, month, data_root_folder).processed
        self.latest_csv = LatestCSV(data_root_folder)

    @staticmethod
    def make_filename(freq):
        if freq in FREQUENCIES:
            return 'df{}.csv'.format(freq)
        else:
            raise ValueError(freq)

    def path(self, freq: str):
        return self.folder / self.make_filename(freq)

def copy_to_latest(year:int, month: int):
     """Copy csv files from folder like *processed/2017/04* to 
        *processed/latest*.
     """    
     if not Date(year, month).is_latest():
         raise ValueError("No files copied, use more recent date.")  
     for freq in FREQUENCIES:    
         src = ProcessedCSV(year, month).path(freq)
         dst = LatestCSV().path(freq)         
         shutil.copyfile(str(src), str(dst))
         print("Updated", dst)

def get_path_in_latest_folder(freq: str): 
    return LatestCSV().path(freq)

if __name__ == "__main__":
    pass
