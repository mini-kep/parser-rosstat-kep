# TODO: edit module docstring
"""File and folder locations for interim and processed CSV files.

Functions based on :class:`csv2df.files.Folder` class methods:

    - :func:`csv2df.files.get_latest_date` returns latest available
      year and month
    - :func:`csv2df.files.locate_csv` retrieves interim CSV file for parsing
      from *data/interim* folder by year and month
    - based on year and month :func:`csv2df.files.get_processed_folder` provides
      location to save parsing result in *data/processed* folder


For housekeeping :mod:`csv2df.files` provides:

 - :func:`csv2df.files.init_dirs` - make directory structure on startup
 - :func:`csv2df.files.copy_latest` - copy CSVs to *latest* folder which
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


from locations.folder import FolderBase, md

__all__ = ['PathHelper', 'DateHelper']

# csv file parameters
ENC = 'utf8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')


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

         (2017, 1), (2017, 2), (2017, 3), (2017, 4), (2017, 5), (2017, 6)]


# folder locations

class Folder(FolderBase):
    def __repr__(self):
        return "Folder({}, {})".format(self.year, self.month)



class PathHelper:
    def locate_csv(year: int=None, month: int=None):
        """Return interim CSV file based on *year* and *month*. Defaults to
           latest year and month.

           Returns:
                pathlib.Path() instance
        """
        year, month = DateHelper.filter_date(year, month)
        folder = Folder(year, month).get_interim_folder()
        csv_path = folder / "tab.csv"
        if csv_path.exists() and csv_path.stat().st_size > 0:
            return csv_path
        else:
            raise FileNotFoundError(
                "File not found or has zero length: {}".format(csv_path))

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
        return DATES

    def get_latest_date():
        """Return year and month for latest available interim data folder.

        Returns:
            (year, month) tuple of two integers

        """
        return Folder.get_latest_date()

    def filter_date(year, month):
        """Set (year, month) to latest date, even if year or month omitted.

        Returns:
            (year, month) tuple of two integers
        """
        latest_year, latest_month = DateHelper.get_latest_date()
        return year or latest_year, month or latest_month


# create local data dirs for DATES


def init_dirs(supported_dates=None):
    """Create required directory structure in *data* folder."""
    if not supported_dates:
        supported_dates = DATES
    for (year, month) in supported_dates:
        f = Folder(year, month)
        md(f.get_interim_folder())
        md(f.get_processed_folder())


if __name__ == "__main__":
    init_dirs()

