# -*- coding: utf-8 -*-
"""Suggested code to read pandas dataframes from stable URL.

To add:
- caching to local file

"""

import pandas as pd


def get_dataframe(freq):
    url_base = "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/{}"
    filename = "df{}.csv".format(freq)
    url = url_base.format(filename)
    # canonical wrapper for pd.read_csv
    return pd.read_csv(url), 
                       #converters={'time_index': pd.to_datetime},
                       #index_col='time_index')

if '__main__' == __name__:
    
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')