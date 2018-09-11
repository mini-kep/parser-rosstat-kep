"""Manage dataset by year and month:

   download(year, month)
   unpack(year, month)
   convert(year, month)
   save_processed(year, month)
   to_latest(year, month)
   to_excel(year, month)
"""

__all__ = ['download', 'unpack', 'convert',
           'save_processed',
           'to_latest', 'to_excel']

import shutil

import kep.load
import kep.dataframe
import kep.runner
import kep.utilities.locations as loc


def echo(func):
    def wrapper(year, month):
        msg = func(year, month)
        print(msg)
    return wrapper


@echo
def download(year: int, month: int):
    filepath = loc.rarfile(year, month)
    return kep.load.download(year, month, filepath)


@echo
def unpack(year: int, month: int):
    filepath = loc.rarfile(year, month)
    folder = loc.raw_folder(year, month)
    return kep.load.unpack(filepath, folder)


@echo
def convert(year: int, month: int):
    folder = loc.raw_folder(year, month)
    filepath = loc.interim_csv(year, month)
    return kep.load.folder_to_csv(folder, filepath)


@echo
def save_processed(year: int, month: int):
    df_dict = kep.runner.get_dataframe_dict(year, month)
    for freq, df in df_dict.items():
        path = loc.processed_csv(year, month, freq)
        df.to_csv(path)
        return f"Saved {year}-{month} dataframe to {path}"


@echo
def to_excel(year: int, month: int):
    df_dict =  kep.runner.get_dataframe_dict(year, month)
    path = loc.xl_location()
    return kep.dataframe.save_excel(path, **df_dict)


@echo
def to_latest(year: int, month: int):
    """Copy CSV files from folder like *processed/2017/04* to *processed/latest*.
    """
    for freq in 'aqm':
        src = loc.processed_csv(year, month, freq)
        dst = loc.latest_csv(freq)
        shutil.copyfile(src, dst)
        print("Updated", dst)
    return f"Latest folder now refers to {year}-{month}"
