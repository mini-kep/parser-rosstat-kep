"""Maintenance tasks after parsing output was created:
    - save xls file
    - copy files to *latest* folder from data/processed/<year>/<month>
"""

import pandas as pd
import shutil

from getter import get_dataframe
from config import PathHelper, DateHelper

__all__ = ['copy_latest', 'save_xls']


def copy_latest():
    """Copy all files from folder like *processed/2017/04* to
       *processed/latest* folder.

       Returns:
           list of files copied
    """
    year, month = DateHelper.get_latest_date()
    print(f'Latest date is {year} {month}.')
    src_folder = PathHelper.get_processed_folder(year, month)
    dst_folder = PathHelper.get_latest_folder()
    copied = []
    for src in [f for f in src_folder.iterdir() if f.is_file()]:
        dst = dst_folder / src.name
        shutil.copyfile(src, dst)
        copied.append(src)
        print('Copied', src)
    print(f'Updated folder {dst_folder}')
    return copied


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
    filepath = PathHelper.get_xl_path()
    to_xls(filepath, dfa, dfq, dfm)
    print('Saved', filepath)


if '__main__' == __name__:
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    save_xls()
