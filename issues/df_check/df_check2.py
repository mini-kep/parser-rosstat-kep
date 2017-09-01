# -*- coding: utf-8 -*-
import numpy as np

# TODO <https://github.com/epogrebnyak/mini-kep/issues/61>

# Check on resulting dataframes dfa, dfq, dfm based on following rules:
#  1. absolute values by month/qtr accumulate to qtr/year (with some delta for rounding)
#  2. rog rates accumulate to yoy (with some delta for rounding)
#
##############################################################################


ANNUAL_FREQUENCY = 'A'


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
    df = levels_df(df)
    return df.resample(freq).sum()


def aggregate_rates(df, freq='A'):
    df = rates_df(df)
    df = (df / 100).cumprod()  # Compute annualized values
    z = df.resample(freq).sum()
    return z / z.shift() * 100


def levels_df(df):
    levels = get_levels(df.columns)
    return df[levels]


def rates_df(df):
    rates = get_rates(df.columns)
    return df[rates]


def build(df):
    return levels_df(df).join(rates_df(df))


def compare_dataframes(df1, agg_func, df2, epsilon):
    """Check consistency of values across month and year dataframes.

    Args:
        df1: Dataframe to aggregate
        agg_func: Aggregation function
        df2: Dataframe to check against
        epsilon: Tolerance for numeric precision

    Returns:
        Boolean value indicating whether all values are within epsilon.
    """
    return np.all(abs((agg_func(df1) - build(df2)).dropna()) < epsilon)


###############################################################################


def month_to_year(dfm):
    df_levels = aggregate_levels(dfm, ANNUAL_FREQUENCY)
    df_rates = aggregate_rates(dfm, ANNUAL_FREQUENCY)
    return df_levels.join(df_rates)


def quarter_to_year(dfq):
    df_levels = aggregate_levels(dfq, ANNUAL_FREQUENCY)
    df_rates = aggregate_rates(dfq, ANNUAL_FREQUENCY)
    return df_levels.join(df_rates)


def runner(feed):
    return np.all(compare_dataframes(*test_case) for test_case in feed)
