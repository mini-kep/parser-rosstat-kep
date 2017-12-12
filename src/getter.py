"""Read canonical dataset from *latest* folder."""

# TODO: add local file caching after import from web
# (?) TODO: with converters 0table may strip 'time_index' columns, not sure

from io import StringIO
from pathlib import Path
import urllib

import pandas as pd

from config import DataFolder

__all__ = ['get_dataframe', 'get_dataframe_from_repo']

# repo file


def read_csv(source):
    """Wrapper for pd.read_csv(). Treats first column at time index.

       Returns:
           pd.DataFrame()
    """
    converter_arg = dict(converters={0: pd.to_datetime}, index_col=0)
    return pd.read_csv(source, **converter_arg)


def make_url(freq):
    filename = "df{}.csv".format(freq)
    return urllib.parse.urljoin(WebSource.BASE_URL, filename)


def get_dataframe_from_repo(freq):
    """Code to read pandas dataframes from stable URL."""
    url = make_url(freq)
    return read_csv(url)

# local path


def proxy(path):
    """A workaround for pandas problem with non-ASCII paths on Windows
       See <https://github.com/pandas-dev/pandas/issues/15086>

       Args:
           path (pathlib.Path) - CSV filepath

       Returns:
           io.StringIO with CSV content
    """
    content = Path(path).read_text()
    return StringIO(content)


def get_dataframe(freq, helper=DataFolder):
    """Read dataframe from local folder"""
    #path = helper.get_csv_in_latest_folder(freq)
    path = str(helper.latest) + '/df' + freq + '.csv'
    filelike = proxy(path)
    return read_csv(filelike)


# make dataframes importable for this module as:
# from getter import dfa, dfq, dfm
dfa, dfq, dfm = (get_dataframe(freq) for freq in 'aqm')

if '__main__' == __name__:
    #dfa = get_dataframe_from_repo('a')
    pass
    z = [varname for df in [dfa, dfq, dfm] for varname in df.columns]
