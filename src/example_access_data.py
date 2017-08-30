# -*- coding: utf-8 -*-
"""Suggested code to read pandas dataframes from stable URL.

Includes:
- caching to local file

This is most simple call:

    # monthly data in *dfm* dataframe
    url_m = "https://raw.githubusercontent.com/epogrebnyak/mini-csv2df/master/data/processed/latest/dfm.csv"
    dfm = pd.read_csv(url_m)

    # quarterly data in *dfq* dataframe
    url_q = "https://raw.githubusercontent.com/epogrebnyak/mini-csv2df/master/data/processed/latest/dfq.csv"
    dfq = pd.read_csv(url_q)

    # annual data in *dfa* dataframe
    url_a = "https://raw.githubusercontent.com/epogrebnyak/mini-csv2df/master/data/processed/latest/dfa.csv"
    dfa = pd.read_csv(url_a)

"""

import pandas as pd


def get_dataframe(freq):
    url = get_url(freq)
    return pd.read_csv(url, 
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')


def read_csv(source):
    """Canonical wrapper for pd.read_csv"""
    return pd.read_csv(source, 
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')


def get_url(freq):
    """Make URL for CSV files by frequency."""
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-csv2df/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    return url_base.format(filename)


def get_dfs_from_web():
    """Get three dataframes from local csv files"""
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    return dfa, dfq, dfm
