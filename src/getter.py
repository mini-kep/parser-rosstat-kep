"""Read canonical dataset from *latest* folder."""

# TODO: add local file caching

import pandas as pd

from pathlib import Path
from io import StringIO

from config import PathHelper

__all__ = ['get_dataframe', 'get_dataframe_from_repo']

# repo file

def read_csv(source):
    """Canonical wrapper for pd.read_csv().
    
       Treats first column at time index. 
       
       Retruns:
           pd.DataFrame()    
    """
    converter_arg = dict(converters={0: pd.to_datetime}, index_col=0) 
    return pd.read_csv(source, **converter_arg)

def make_url(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    return url_base.format(filename)


def get_dataframe_from_repo(freq):
    """Suggested code to read pandas dataframes from 'mini-kep' stable URL."""
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


def get_dataframe(freq, helper=PathHelper):
    """Read dataframe from local folder"""
    path = helper.get_csv_in_latest_folder(freq)
    filelike = proxy(path)
    return read_csv(filelike)

# make df's importable from here
dfa, dfq, dfm = (get_dataframe(freq) for freq in 'aqm')

if '__main__' == __name__:
    #dfa = get_dataframe_from_repo('a')
    pass