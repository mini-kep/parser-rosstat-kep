# -*- coding: utf-8 -*-
"""Common code to read pandas dataframes from stable URL or local CSV files."""

import pandas as pd
from pathlib import Path

# if in package, can import this from src.kep.cfg.py
FOLDER_LATEST_CSV  = Path(__file__).parents[2] / "data" / "processed" / "latest"
FOLDER_LATEST_JSON = Path(__file__).parents[2] / "data" / "processed" / "latest_json"
FILENAMES = {freq:"df{}.csv".format(freq) for freq in "aqm"}

def error_frequency(freq):
    raise KeyError("Supported frequencies are 'a', 'q' or 'm'."
                   "\nProvided: {}".format(freq))    

def csv_path(freq, folder = FOLDER_LATEST_CSV):
    try:
        return folder / FILENAMES[freq]
    except KeyError:
        error_frequency(freq)

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
    """Get three dataframes from local csv files"""
    dfa = read_csv_safe_long_name(csv_path('a'))
    dfq = read_csv_safe_long_name(csv_path('q'))
    dfm = read_csv_safe_long_name(csv_path('m'))
    return dfa, dfq, dfm
    
def get_url(freq):
    """Make URL for CSV files"""
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    try:                                                                                                   
        return url_base.format(FILENAMES[freq])
    except KeyError:
        error_frequency(freq)        

def get_dfs_from_web():
    """Get three dataframes from local csv files"""
    dfa = read_csv(get_url('a'))
    dfq = read_csv(get_url('q'))
    dfm = read_csv(get_url('m'))
    return dfa, dfq, dfm

# IDEA: import local copy of "df*.csv" and update from web if necessary 
#       see oil and CBR repositories for that 

def save_json(self, folder_path):
    ext = ".json"
    param = dict(orient="records")
    self.dfa.to_csv(folder_path / 'dfa'+ ext, **param)
    self.dfq.to_csv(folder_path / 'dfq'+ ext, **param)
    self.dfm.to_csv(folder_path / 'dfm'+ ext, **param)
    print("Saved dataframes as json to", folder_path)

if __name__ == "__main__":
    # FIXME: must quarantee 'latest' is updated 
    dfa1, dfq1, dfm1 = get_dfs_from_web()
    dfa, dfq, dfm = get_dfs()
    
    # FIXME get_dfs_from_web() may be slow, otherwise could be a good test to compare dfa1 to dfa, etc    
    assert dfa1.equals(dfa)
    assert dfq1.equals(dfq)
    assert dfm1.equals(dfm)   