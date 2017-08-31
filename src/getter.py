"""Read canonical dataset from *latest* folder."""

from pathlib import Path
from io import StringIO
import pandas as pd

from config import PathHelper

__all__ = ['get_dataframe']


def read_csv(source):
    """Canonical wrapper for pd.read_csv()."""
    return pd.read_csv(source,
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')


def get_dataframe(freq):
    """Read dataframe from local folder"""
    path = PathHelper.get_latest_csv(freq)
    # a workaround for Windows problem with non-ASCII paths
    # https://github.com/pandas-dev/pandas/issues/15086
    content = Path(path).read_text()
    filelike = StringIO(content)
    return read_csv(filelike)


def make_url(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    return url_base.format(filename)


def get_dataframe_from_web(freq):
    """Suggested code to read pandas dataframes from stable URL."""
    url = make_url(freq)
    return read_csv(url)

# TODO: add local file caching


if '__main__' == __name__:
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
