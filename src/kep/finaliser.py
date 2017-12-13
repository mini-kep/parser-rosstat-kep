"""Save xls file."""

import pandas as pd
import shutil

from kep.getter import get_dataframe
import kep.config as config


__all__ = ['save_xls']


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
    filepath = config.XL_PATH
    to_xls(filepath, dfa, dfq, dfm)
    print('Saved', filepath)


# FIXME: vulnerable to proper date, attempts working in empty directory
def copy_latest():
    """Copy csv files from folder like
           *processed/2017/04*
       to
           *processed/latest* folder.
    """
    year, month = config.LATEST_DATE
    csv_file = config.ProcessedCSV(year, month)
    latest = config.Latest
    for freq in config.FREQUENCIES:
        src = csv_file.path(freq)
        dst = latest.csv(freq)
        shutil.copyfile(src, dst)
        print('Copied', src)


if '__main__' == __name__:
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    save_xls()
