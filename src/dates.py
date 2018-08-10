import random
import pandas as pd


def supported_dates(start_date='2009-04', exclude_dates=['2013-11']):
    """Get a list of (year, month) tuples starting from (2009, 4) up to
       a previous recent month. This a 'supported date list'.
       Excludes (2013, 11) - no archive for this month.
    Returns:
        List of (year: int, month: int) tuples.
    """
    end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
    dates = pd.date_range(start_date, end_date, freq='MS')
    exclude = map(pd.to_datetime, exclude_dates)
    return [(date.year, date.month) for date in dates.drop(exclude)]


SUPPORTED_DATES = supported_dates()

def random_date():
    return random.choice(SUPPORTED_DATES[:-2])


def assert_supported(year, month):
    if not (year, month) in SUPPORTED_DATES:
        raise ValueError(year, month)


def date_span(start_date, end_date):
    supported_date_list = supported_dates()
    return [(date.year, date.month) for date in
            pd.date_range(start_date, end_date, freq='MS')
            if (date.year, date.month) in supported_date_list]


def is_latest(year: int, month: int, offset=2):
    return (year, month) in SUPPORTED_DATES[:-offset]
