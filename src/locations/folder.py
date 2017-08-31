"""Helper class FolderBase to navigate through */data* directory structure.

   Also includes copy_latest() housekeeping function.
"""

from pathlib import Path
import shutil

CSV_FILENAME = 'tab.csv'
XL_FILENAME = 'kep.xlsx'


def find_repo_root():
    """Returns root folder for repository.

    Current file is assumed to be at:
        <repo_root>/src/locations

    Must go to levels up from current file to reach repo root.
    """
    levels_up = 2
    return Path(__file__).parents[levels_up]


def md(folder, i=0):
    """Create *folder* if not exists.
       Also create parent folder if not exists."""
    if i > 3:
        ValueError("Cannot create path, iteration too deep: {}".format(folder))
    if not folder.exists():
        parent = folder.parent
        if not parent.exists():
            i += 1
            md(parent, i)
        folder.mkdir()


def get_unrar_binary():
    root = find_repo_root()
    unrar_filename = "UnRAR.exe"
    return str(root / 'bin' / unrar_filename)


def get_xl_filepath():
    root = find_repo_root()
    return str(root / 'output' / XL_FILENAME)


def get_latest_csv(freq):
    return str(FolderBase.latest / "df{}.csv".format(freq))


class FolderBase:
    root = find_repo_root()
    raw = root / 'data' / 'raw'
    interim = root / 'data' / 'interim'
    processed = root / 'data' / 'processed'
    latest = root / 'data' / 'processed' / 'latest'

    def __init__(self, year=None, month=None):
        self.year, self.month = year, month

    @classmethod
    def get_latest_date(cls):
        root = cls.interim

        def max_subfolder(folder):

            subfolders = [f.name for f in folder.iterdir() if f.is_dir()]
            return max(map(int, subfolders))
        year = max_subfolder(root)

        subfolder = root / str(year)
        month = max_subfolder(subfolder)
        return year, month

    def make_dirs(self):
        for folder in [self.get_raw_folder(),
                       self.get_interim_folder(),
                       self.get_processed_folder()]:
            md(folder)

    def _local_folder(self, parent_folder):
        folder = parent_folder / str(self.year) / str(self.month).zfill(2)
        return folder

    def get_raw_folder(self):
        return self._local_folder(self.raw)

    def get_interim_folder(self):
        return self._local_folder(self.interim)

    def get_interim_csv(self):
        return self.get_interim_folder() / CSV_FILENAME

    def get_processed_folder(self):
        return self._local_folder(self.processed)

    def copy_tab_csv(self):
        src = self.get_raw_folder() / CSV_FILENAME
        dst = self.get_interim_folder() / CSV_FILENAME
        from shutil import copyfile
        copyfile(src, dst)
        return True

    @staticmethod
    def is_valid_filepath(path):
        return bool(path.exists() and path.stat().st_size > 0)

    def __repr__(self):
        return "FolderBase({}, {})".format(self.year, self.month)


# housekeeping  - copy contents to 'processed/latest' folder

def copy_latest():
    """Copy all files from folder like *processed/2017/04* to
       *processed/latest* folder.

       Returns:
           list of files copied
    """
    year, month = FolderBase.get_latest_date()
    src_folder = FolderBase(year, month).get_processed_folder()
    dst_folder = FolderBase.latest
    copied = []
    for src in [f for f in src_folder.iterdir() if f.is_file()]:
        dst = dst_folder / src.name
        shutil.copyfile(src, dst)
        copied.append(dst)
    print("Latest date is", year, month)
    print("Updated folder", FolderBase.latest)
    return copied
