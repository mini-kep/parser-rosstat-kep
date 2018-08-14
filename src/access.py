import kep
from pathlib import Path
from io import StringIO
import pandas as pd

def read_csv(source):
    """Wrapper for pd.read_csv(). Treats first column as time index.
       Returns:
           pd.DataFrame()
    """
    converter_arg = dict(converters={0: pd.to_datetime}, index_col=0)
    return pd.read_csv(source, **converter_arg)


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


def read_dataframe(path):
    filelike = proxy(path)
    return read_csv(filelike)   
 

def get_dataframe(year, month, freq):
    """Read processed dataframe from local folder by *year* and *month*."""
    path = kep.processed_csv(year, month, freq)
    return read_dataframe(path)


def get_df_latest(freq):
    """Read processed dataframe from local *latest* folder."""
    path = kep.latest_csv(freq)
    return read_dataframe(path)


def get_dataframe_from_web(frequency):
    """Read dataframe by frequency from stable URL."""
    if frequency not in ['a', 'q', 'm']:
        raise ValueError(f'{frequency} must be a, q or m')
    url = ('https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/'
          f'master/data/processed/latest/df{frequency}.csv')
    return pd.read_csv(url, converters={0: pd.to_datetime}, index_col=0)

