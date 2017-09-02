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
    """Aggregates a dataframe that has levels columns.

    Args: 
        df: A dataframe to aggregate. It is subsetted to have only columns that
        are levels.
        freq: The frequency to resample to. The default is annual.

    Returns:
        An aggregated dataframe depending on the frequency.
    """
    df = subset_levels(df)
    return df.resample(freq).sum()


def aggregate_rates(df, freq='A'):
    """Aggregates a dataframe that has rates columns.

    Args:
        df: A dataframe to aggregate. It is subsetted to have only columns that
        are rates..
        freq: The frequency to resample to. The default is annual.

    Returns:
        An aggregated dataframe depending on the frequency.
    """
    df = subset_rates(df)
    df = (df / 100).cumprod()  # Compute annualized values
    z = df.resample(freq).sum()
    return z / z.shift() * 100


def subset_levels(df):
    """Subsets a dataframe with levels columns only."""
    return df[get_levels(df.columns)]


def subset_rates(df):
    """Subsets a dataframe with rates columns only."""
    return df[get_rates(df.columns)]


def merge_rates_levels(df):
    """Combines a subsetted levels and rates dataframe (without aggregating)."""
    return subset_levels(df).join(subset_rates(df))


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
    return np.all(abs((agg_func(df1) - merge_rates_levels(df2)).dropna()) < epsilon)


def month_to_year(dfm):
    """Aggregates a monthly dataframe to an annual one."""
    df_levels = aggregate_levels(dfm, ANNUAL_FREQUENCY)
    df_rates = aggregate_rates(dfm, ANNUAL_FREQUENCY)
    return df_levels.join(df_rates)


def quarter_to_year(dfq):
    """Aggregates a quarterly dataframe to an annual one."""
    df_levels = aggregate_levels(dfq, ANNUAL_FREQUENCY)
    df_rates = aggregate_rates(dfq, ANNUAL_FREQUENCY)
    return df_levels.join(df_rates)


def runner(feed):
    """Tests a list of tuples to pass as an argument to the compare_dataframes()
        function.

    Args:
        feed: (df1, accum, df2, epsilon)

    Returns:
        A boolean, true if all tests are successful.
    """
    return np.all(compare_dataframes(*test_case) for test_case in feed)


def column_to_aggfunc(column, dfm, dfq):
    """Chooses an appropriate aggregation function, depending on the whether
        the column exists in the dataframe.
    
    Args:
        column: String containing the column name
        dfm: Monthly dataframe
        dfq: Quarterly dataframe

    Returns:
        A function - either month_to_year or quarter_to_year
    """
    if column in dfm.columns:
        return month_to_year
    elif column not in dfm.columns and column in dfq.columns:
        return quarter_to_year
    else:
        raise ValueError("Unknown variable")
