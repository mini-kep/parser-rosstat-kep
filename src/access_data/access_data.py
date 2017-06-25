# -*- coding: utf-8 -*-
"""Common code to read pandas dataframes from stable URL or local CSV files."""

from datetime import datetime
import pandas as pd
from pathlib import Path

# if in package, can import this from src.kep.cfg.py
FOLDER_LATEST_CSV  = Path(__file__).parents[2] / "data" / "processed" / "latest"
FOLDER_LATEST_JSON = Path(__file__).parents[2] / "data" / "processed" / "latest_json"
FILENAMES = {freq:"df{}.csv".format(freq) for freq in "aqm"}

#IDEA: re-generate dfa with timestamp 'time_index' as opposed to int year 
#      to make import uniform, without to_ts()
def to_ts(year):
    return pd.Timestamp(datetime(int(year),12,31)) 

def read_csv(source):
    """Canonical wrapper for pd.read_csv"""
    return pd.read_csv(source, converters = {'time_index':pd.to_datetime}, 
                               index_col = 'time_index')
    
def read_csv_safe_long_name(source):
    """Works safely on long directory names"""
    assert isinstance(source, Path)
    with source.open() as buf:
        return read_csv(buf)
 
def get_dfs():        
    dfa = pd.read_csv(get_csv_path('a').open(), converters = {'year':to_ts}, index_col = 'year')    
    dfq =  read_csv_safe_long_name(get_csv_path('q'))
    dfm =  read_csv_safe_long_name(get_csv_path('m'))
    return dfa, dfq, dfm
    
def get_urls():
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/"
    assert url_base.endswith("/")
    return {freq: url_base + filename for freq, filename in FILENAMES.items()}

def get_dfs_from_web():
    return get_dfs(sources=get_urls())

def get_csv_path(freq, folder = FOLDER_LATEST_CSV):
    return folder / FILENAMES[freq]


# FIMXE: import local copy of "df*.csv" and update from web if necessary 
#        see oil and CBR repositories for that 

def save_json(self, folder_path):
    ext = ".json"
    param = dict(orient="records")
    self.dfa.to_csv(folder_path / 'dfa'+ ext, **param)
    self.dfq.to_csv(folder_path / 'dfq'+ ext, **param)
    self.dfm.to_csv(folder_path / 'dfm'+ ext, **param)
    print("Saved dataframes as json to", folder_path)

if __name__ == "__main__":
    #IDEA: get_dfs_from_web() is slow, otherwise could be a good test to compare dfa1 to dfa, etc
    #dfa1, dfq1, dfm1 = get_dfs_from_web()
    dfa, dfq, dfm = get_dfs()
    #TODO: compare to webs