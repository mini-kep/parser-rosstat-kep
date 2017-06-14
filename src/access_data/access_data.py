"""Common code to read pandas dataframes from stable URL or local CSV files."""

from datetime import datetime
import pandas as pd
from pathlib import Path

#IDEA: re-generate dfa with timestamp 'time_index' as opposed to int year 
#      to make import uniform, without to_ts()
def to_ts(year):
    return pd.Timestamp(datetime(int(year),12,31)) 

def get_dfs(sources):        
    dfa = pd.read_csv(sources['a'], converters = {'year':to_ts}, index_col = 'year')    
    dfq = pd.read_csv(sources['q'], converters = {'time_index':pd.to_datetime}, index_col = 'time_index')
    dfm = pd.read_csv(sources['m'], converters = {'time_index':pd.to_datetime}, index_col = 'time_index')
    return dfa, dfq, dfm

FILENAMES = {freq:"df{}.csv".format(freq) for freq in "aqm"}
    
def get_urls():
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/"
    assert url_base.endswith("/")
    return {freq: url_base + filename for freq, filename in FILENAMES.items()}

def get_dfs_from_web():
    return get_dfs(sources=get_urls())

def get_paths():
    data_dir_path = Path(__file__).parents[2] / "data" / "processed" / "latest"
    return {freq: data_dir_path / filename for freq, filename in FILENAMES.items()}

def get_dfs_from_local():
    return get_dfs(sources=get_paths())

# FIMXE: import local copy of "df*.csv" and update from web if necessary 
#        see oil and CBR repositories for that 

if __name__ == "__main__":
    #IDEA: get_dfs_from_web() is slow, otherwise could be a good test to compare dfa1 to dfa, etc
    #dfa1, dfq1, dfm1 = get_dfs_from_web()
    dfa, dfq, dfm = get_dfs_from_local()