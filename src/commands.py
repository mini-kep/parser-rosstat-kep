"""Manage dataset by year and month:

   download(year, month)
   unpack(year, month)
   make_interim_csv(year, month)
   parse_and_save(year, month)
   to_latest(year, month)
   to_excel(year, month)

File access:
    get_dataframe(year, month, freq)

"""
from pathlib import Path
from io import StringIO
import pandas as pd
import shutil

import helper.locations as locations
import loader

def echo(func):
    def wrapper(*arg, **kwarg):
        msg = func(*arg, **kwarg)
        print(msg)
    return wrapper


@echo
def download(year, month, force=False):
    filepath = locations.rarfile(year, month)
    return loader.download(year, month, filepath, force)


@echo
def unpack(year, month, force=False):
    filepath = locations.rarfile(year, month)
    folder = locations.raw_folder(year, month)
    return loader.unpack(filepath, folder, force)


@echo
def make_interim_csv(year, month, force=False):
    folder = locations.raw_folder(year, month)
    filepath = locations.interim_csv(year, month)
    return loader.folder_to_csv(folder, filepath)

#
#@echo
#def parse_and_save(year, month, force=False):
#    dfs = parse_to_dataframes(year, month)
#    return save(year, month, *dfs)


#def parse_to_dataframes(year, month):
#    common_dicts, segment_dicts = get_parsing_parameters('param//instructions.yml') 
#    base_mapper = get_mapper('param//base_units.yml')
#    tables = main(common_dicts, segment_dicts, base_mapper)  
#    values = datapoints(tables)
#    return s.dataframes()


def save(year, month, dfa, dfq, dfm):
    for df, freq in zip([dfa, dfq, dfm], 'aqm'):
        path = locations.processed_csv(year, month, freq)
        df.to_csv(path)
        return "Saved dataframe to {}".format(path)


@echo
def to_excel(year: int, month: int):
    dfs = {f'df{freq}': get_dataframe(year, month, freq) for freq in 'aqm'}
    path = locations.xl_location()
    return finisher.save_excel(path, **dfs)


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


def get_dataframe(year, month, freq):
    """Read dataframe from local folder"""
    path = processed_csv(year, month, freq)
    filelike = proxy(path)
    return read_csv(filelike)
