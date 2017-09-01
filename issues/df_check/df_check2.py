# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from io import StringIO


# TODO <https://github.com/epogrebnyak/mini-kep/issues/61>

# Check on resulting dataframes dfa, dfq, dfm based on following rules:
#  1. absolute values by month/qtr accumulate to qtr/year (with some delta for rounding)
#  2. rog rates accumulate to yoy (with some delta for rounding)
#
########################################################################################


def get_levels(columns):
    """Find the columns that are levels.
    
    Args:
        columns: List of column names from dataframe.

    Returns:
        Filtered list of levels.
    """
    return [column for column in columns
            if ('_bln_rub' in column or '_bln_usd' in column)
            and 'GOV' not in column]


def get_rates(columns):
    """Find the columns that are rates.
    
    Args:
        columns: List of column names from dataframe.

    Returns:
        Filtered list of rates.
    """
    return [column for column in columns 
            if '_rog' in column and 'GOV' not in column]


def aggregate_levels(df, freq='A'):
    return df.resample(freq).sum()


def aggregate_rates(df, freq='A'):
    df = (df / 100).cumprod()  # Compute annualized values
    z = df.resample(freq).sum()
    z = z / z.shift() * 100
    return z


def build_levels_df(df):
    levels = get_levels(df.columns)
    return df[levels]


def build_rates_df(df):
    rates = get_rates(df.columns)
    return df[rates]


def compare_dataframes(df1, agg_func, df2, epsilon):
    """Check consistency of values across month and year dataframes.
    
    Args:
        df1: Dataframe with monthly values
        agg_func: Dataframe with annual values
        df2: Dataframe with quarterly values (unused)
        epsilon: Tolerance for numeric precision
        
    Returns:
        Boolean value indicating whether all values are within epsilon.
    """
    if agg_func.__name__ == 'aggregate_levels':
        columns = get_levels(df1.columns)
        df1 = build_levels_df(df1)
    return np.all(abs((agg_func(df1[columns]) - df2[columns]).dropna()) < epsilon)
