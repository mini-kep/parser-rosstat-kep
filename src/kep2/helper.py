"""File and folder locations for interim and processed CSV files.

Functions based on :class:`kep.files.Folder` class methods:

    - :func:`kep.files.get_latest_date` returns latest available
      year and month
    - :func:`kep.files.locate_csv` retrieves interim CSV file for parsing
      from *data/interim* folder by year and month
    - based on year and month :func:`kep.files.get_processed_folder` provides
      location to save parsing result in *data/processed* folder


For housekeeping :mod:`kep.files` provides:

 - :func:`kep.files.init_dirs` - make directory structure on startup
 - :func:`kep.files.copy_latest` - copy CSVs to *latest* folder which
   has stable URL


For reference - data directory structure::

    \\data
      \\interim
          \\2017
          \\2016
          \\...
      \\processed
          \\latest
          \\latest_json (may be depreciated)
          \\2017
          \\2016
          \\...
"""

from pathlib import Path
import shutil

__all__ = ['locate_csv', 'get_processed_folder',
           'filled_dates', 'get_latest_date']

# csv file parameters
ENC = 'utf8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')

# we are in src/kep
levels_up = 2
data_folder = Path(__file__).parents[levels_up] / 'data'

# FIXME: hardcoded constant will not update to new months
DATES = [(2009, 4), (2009, 5), (2009, 6),
         (2009, 7), (2009, 8), (2009, 9), (2009, 10), (2009, 11), (2009, 12),

         (2010, 1), (2010, 2), (2010, 3), (2010, 4), (2010, 5), (2010, 6),
         (2010, 7), (2010, 8), (2010, 9), (2010, 10), (2010, 11), (2010, 12),

         (2011, 1), (2011, 2), (2011, 3), (2011, 4), (2011, 5), (2011, 6),
         (2011, 7), (2011, 8), (2011, 9), (2011, 10), (2011, 11), (2011, 12),

         (2012, 1), (2012, 2), (2012, 3), (2012, 4), (2012, 5), (2012, 6),
         (2012, 7), (2012, 8), (2012, 9), (2012, 10), (2012, 11), (2012, 12),

         (2013, 1), (2013, 2), (2013, 3), (2013, 4), (2013, 5), (2013, 6),
         (2013, 7), (2013, 8), (2013, 9), (2013, 10),  # missing (2013, 11)
         (2013, 12),

         (2014, 1), (2014, 2), (2014, 3), (2014, 4), (2014, 5), (2014, 6),
         (2014, 7), (2014, 8), (2014, 9), (2014, 10), (2014, 11), (2014, 12),

         (2015, 1), (2015, 2), (2015, 3), (2015, 4), (2015, 5), (2015, 6),
         (2015, 7), (2015, 8), (2015, 9), (2015, 10), (2015, 11), (2015, 12),

         (2016, 1), (2016, 2), (2016, 3), (2016, 4), (2016, 5), (2016, 6),
         (2016, 7), (2016, 8), (2016, 9), (2016, 10), (2016, 11), (2016, 12),

         (2017, 1), (2017, 2), (2017, 3), (2017, 4), (2017, 5)]

# end user functions


def filled_dates():
    return DATES


def get_latest_date():
    """Return year and month for latest available interim data folder.

    Returns:
        (year, month) tuple of two integers

    """
    return Folder.get_latest_date()


def locate_csv(year: int=None, month: int=None):
    """Return interim CSV file based on *year* and *month*.

    Returns:
        pathlib.Path() instance
    """
    folder = Folder(year, month).get_interim_folder()
    csv_path = folder / "tab.csv"
    if csv_path.exists() and csv_path.stat().st_size > 0:
        return csv_path
    else:
        raise FileNotFoundError(
            "Not found or has zero length: {}".format(csv_path))


def get_processed_folder(year, month):
    """Return processed CSV file folder based on *year* and *month*.

    The processed CSV file folder is used by Frames class
    to write output files (dfa.csv, dfq.csv, dfm.csv).

    Returns:
        pathlib.Path() instance

    """
    return Folder(year, month).get_processed_folder()


# folder locations
class Folder:
    interim = data_folder / 'interim'
    processed = data_folder / 'processed'
    latest = processed / 'latest'
    supported_dates = DATES

    @classmethod
    def get_latest_date(cls):
        root = cls.interim

        def max_subfolder(folder):
            _lst = [f.name for f in folder.iterdir() if f.is_dir()]
            return int(max(_lst))
        year = max_subfolder(root)
        _subfolder = root / str(year)
        month = max_subfolder(_subfolder)
        return year, month

    @classmethod
    def filter_date(cls, year, month):
        # mask with latest date
        if not year or not month:
            year, month = cls.get_latest_date()
        # check if date is available
        if (year, month) in cls.supported_dates:
            return year, month
        else:
            msg = "Year and month not found: {} {}".format(year, month)
            raise ValueError(msg)

    def __init__(self, year=None, month=None):
        self.year, self.month = Folder.filter_date(year, month)

    def _local_folder(self, root):
        return root / str(self.year) / str(self.month).zfill(2)

    def get_interim_folder(self):
        return self._local_folder(root=self.interim)

    def get_processed_folder(self):
        return self._local_folder(root=self.processed)

    def __repr__(self):
        return "Folder({}, {})".format(self.year, self.month)


# create local data dirs for DATES

def md(folder):
    """Create *folder* if not exists.
       Also create parent folder if needed. """
    if not folder.exists():
        parent = folder.parent
        if not parent.exists():
            parent.mkdir()
        folder.mkdir()


def init_dirs(supported_dates=None):
    """Create required directory structure in *data* folder."""
    if not supported_dates:
        supported_dates = DATES
    for (year, month) in supported_dates:
        f = Folder(year, month)
        md(f.get_interim_folder())
        md(f.get_processed_folder())


# housekeeping  - copy contents to 'processed/latest' folder

def copy_latest():
    """Copy all files from folder like *processed/2017/04* to
       *processed/latest* folder.

       Returns:
           list of files copied
    """
    year, month = get_latest_date()
    src_folder = get_processed_folder(year, month)
    copied = []
    for src in [f for f in src_folder.iterdir() if f.is_file()]:
        dst = Folder.latest / src.name
        shutil.copyfile(src, dst)
        copied.append(dst)
    print("Updated folder", Folder.latest)
    return copied


if __name__ == "__main__":
    init_dirs()
    copy_latest()
