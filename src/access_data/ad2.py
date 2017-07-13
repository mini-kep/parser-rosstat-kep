"""Common code to read pandas dataframes from stable URL or local CSV files."""

import pandas as pd

def read(source):
    """Canonical wrapper for pd.read_csv"""
    return pd.read_csv(source, converters={'time_index': pd.to_datetime},
                       index_col='time_index')

def get_url(freq):
    """Make URL for CSV files"""
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    return url_base.format(filename)


def get_dfs_from_web():
    """Get three dataframes from local csv files"""
    dfa = read_csv(get_url('a'))
    dfq = read_csv(get_url('q'))
    dfm = read_csv(get_url('m'))
    return dfa, dfq, dfm

#TODO: save to local cache, update cache
