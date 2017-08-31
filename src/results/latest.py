"""Read canonical dataset from *latest* folder."""

from pathlib import Path
from io import StringIO
import pandas as pd

from locations.folder import get_latest_csv
from locations.folder import get_xl_filepath

__all__ = ['get_dataframe', 'save_xls']


def read_csv(source):
    """Canonical wrapper for pd.read_csv()."""
    return pd.read_csv(source,
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')


def get_dataframe(freq):
    """Read dataframe from local folder"""
    path = get_latest_csv(freq)
    # a workaround for Windows problem
    # https://github.com/pandas-dev/pandas/issues/15086
    content = Path(path).read_text()
    filelike = StringIO(content)
    return read_csv(filelike)


def to_xls(filepath, dfa, dfq, dfm):
    """Save dataframes *dfa, dfq, dfm* in .xlsx *filepath*."""
    with pd.ExcelWriter(filepath) as writer:
        dfa.to_excel(writer, sheet_name='year')
        dfq.to_excel(writer, sheet_name='quarter')
        dfm.to_excel(writer, sheet_name='month')
        # TODO: add variable names
        #self.df_vars().to_excel(writer, sheet_name='variables')


def save_xls():
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    filepath = get_xl_filepath()
    to_xls(filepath, dfa, dfq, dfm)


if '__main__' == __name__:
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    save_xls()
