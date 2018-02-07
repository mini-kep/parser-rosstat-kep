"""Dates for the project.

Constant:
    SUPPORTED_DATES

Method:
    is_supported_date()
"""

import pandas as pd


def supported_dates(start_date='2009-04', exclude_dates=['2013-11']):
    """Get a list of (year, month) tuples starting from (2009, 4)
       up to a previous recent month.

       Excludes (2013, 11) - no archive for this month.

    Returns:
        List of (year, month) tuples.
    """
    end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
    dates = pd.date_range(start_date, end_date, freq='MS')
    exclude = map(pd.to_datetime, exclude_dates)
    return [(date.year, date.month) for date in dates.drop(exclude)]


SUPPORTED_DATES = supported_dates()


def is_supported_date(year, month):
    if (year, month) in SUPPORTED_DATES:
        return True
    else:
        raise ValueError(f'<{year}, {month}> is not a supported date.')
