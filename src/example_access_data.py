# -*- coding: utf-8 -*-
"""Suggested code to read pandas dataframes from stable URL."""

# TODO:
# - caching to local file

import pandas as pd


def make_url(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    return url_base.format(filename)


def read_csv(source):
    """Canonical wrapper for pd.read_csv()."""
    return pd.read_csv(source,
                       converters={'time_index': pd.to_datetime},
                       index_col='time_index')


def get_dataframe(freq):
    url = make_url(freq)
    return read_csv(url)


if '__main__' == __name__:
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
