# -*- coding: utf-8 -*-

import pandas as pd

def compose_url(freq):
    """Make URL for CSV files by frequency."""
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    return url_base.format(filename)


def get_any_dataframe(source):
    """Canonical wrapper for pd.read_csv"""
    return pd.read_csv(source, 
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')


def get_dataframe(freq):
    return get_any_dataframe(compose_url(freq))


def get_dfs_from_web():
    """Get three dataframes from local csv files"""
    dfs = {}
    for k in ['a', 'q', 'm']:
        dfs[k] = get_dataframe(k)
    return dfs
