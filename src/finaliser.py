"""Maintenance tasks after parsing output was created:
    - save xls file
    - copy files to *latest* folder from data/processed/<year>/<month>
"""

import pandas as pd
import shutil

from getter import get_dataframe
from config import PathHelper
from config import DateHelper


__all__ = ['copy_latest', 'save_xls']


def get_latest_date(dhelper=DateHelper):
    return DateHelper.get_latest_date()


def copy_latest(helper=PathHelper):
    """Copy all files from folder like *processed/2017/04* to
       *processed/latest* folder.

       Returns:
           list of files copied
    """
    year, month = get_latest_date()
    src_folder = helper.get_processed_folder(year, month)
    dst_folder = helper.get_latest_folder()
    copied = []
    src_files = [f for f in src_folder.iterdir() if f.is_file()]
    for src in src_files:
        dst = dst_folder / src.name
        shutil.copyfile(src, dst)
        copied.append(src)
        print('Copied', src)
    print(f'Source folder {src_folder}')
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


def save_xls(helper=PathHelper):
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    filepath = helper.get_xl_path()
    to_xls(filepath, dfa, dfq, dfm)
    print('Saved', filepath)


if '__main__' == __name__:
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    save_xls()
