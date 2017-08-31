# TODO: edit module docstring
"""File and folder locations for interim and processed CSV files.

Functions based on :class:`csv2df.locations.folder.FolderBase` class methods:

    - :func:`DateHelper.get_latest_date` returns latest available
      year and month
    - :func:`PathHelper.locate_csv` retrieves interim CSV file for parsing
      from *data/interim* folder by year and month
    - based on year and month :func:`get_processed_folder` provides
      location to save parsing result in *data/processed* folder


For housekeeping :mod:`csv2df.helpers` provides:

 - :func:`init_dirs` - make directory structure on startup
 - :func:`locations.folder.copy_latest` - copy CSVs to *latest* folder which
   has stable URL


For reference - data directory structure::

    \\data
      \\interim
          \\2017
          \\2016
          \\...
      \\processed
          \\latest
          \\2017
          \\2016
          \\...
"""


import pandas as pd
from locations.folder import FolderBase, md

__all__ = ['PathHelper', 'DateHelper', 'init_dirs']

# csv file parameters
ENC = 'utf8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')

# folder locations

class Folder(FolderBase):
    def __repr__(self):
        return "Folder({}, {})".format(self.year, self.month)


class PathHelper:
    
    def locate_latest_csv():
        year, month = DateHelper.get_latest_date()
        return PathHelper.locate_csv(year, month)        
   
    
    def locate_csv(year: int, month: int):
        """Return interim CSV file based on *year* and *month*. Defaults to
           latest year and month.

           Returns:
                pathlib.Path() instance
        """
        if (year, month) not in DateHelper.get_supported_dates():
            raise ValueError(year, month)
        folder = Folder(year, month).get_interim_folder()
        csv_path = folder / "tab.csv"
        if not csv_path.exists():
            raise FileNotFoundError(csv_path)
        elif csv_path.stat().st_size == 0:   
            raise FileNotFoundError('File has zero length: {}'.format(csv_path))
        else:    
            return csv_path
        

    def get_processed_folder(year, month):
        """Return processed CSV file folder based on *year* and *month*.

        The processed CSV file folder is used by Frames class
        to write output files (dfa.csv, dfq.csv, dfm.csv).

        Returns:
            pathlib.Path() instance

        """
        return Folder(year, month).get_processed_folder()


class DateHelper:

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
         
    def get_latest_date():
        """Return year and month for latest available interim data folder.

        Returns:
            (year, month) tuple of two integers

        """
        return Folder.get_latest_date()

#    def filter_date(year, month):
#        """Set (year, month) to latest date, even if year or month omitted.
#
#        Returns:
#            (year, month) tuple of two integers
#        """
#        latest_year, latest_month = DateHelper.get_latest_date()
#        return year or latest_year, month or latest_month


# create local data dirs for DATES

def init_dirs():
    """Create required directory structure in *data* folder."""
    supported_dates = DateHelper.get_supported_dates()
    for (year, month) in supported_dates:
        f = Folder(year, month)
        md(f.get_interim_folder())
        md(f.get_processed_folder())


if __name__ == "__main__":
    init_dirs()
