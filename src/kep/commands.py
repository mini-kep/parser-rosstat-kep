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

import kep
import kep.util.locations as locations


def echo(func):
    def wrapper(*arg, **kwarg):
        msg = func(*arg, **kwarg)
        print(msg)
    return wrapper


@echo
def download(year, month, force=False):
    filepath = locations.rarfile(year, month)
    return kep.load.download(year, month, filepath, force)


@echo
def unpack(year, month, force=False):
    filepath = locations.rarfile(year, month)
    folder = locations.raw_folder(year, month)
    return kep.load.unpack(filepath, folder, force)


@echo
def convert(year, month):
    folder = locations.raw_folder(year, month)
    filepath = locations.interim_csv(year, month)
    return kep.load.folder_to_csv(folder, filepath)


@echo
def save_processed(year, month):
    df_dict = kep.get_dataframe_dict(year, month)
    for freq, df in df_dict.items():
        path = locations.processed_csv(year, month, freq)
        df.to_csv(path)
        return f"Saved {year}-{month} dataframe to {path}"
    

@echo
def to_excel(year: int, month: int):
    df_dict = kep.get_dataframe_dict(year, month)
    path = locations.xl_location()
    return kep.dataframe.save_excel(path, **df_dict)


@echo
def to_latest(year: int, month: int):
    """Copy CSV files from folder like *processed/2017/04* to *processed/latest*.
    """
    for freq in 'aqm':
        src = locations.processed_csv(year, month, freq)
        dst = locations.latest_csv(freq)
        shutil.copyfile(src, dst)
        print("Updated", dst)
    return f"Latest folder now refers to {year}-{month}"