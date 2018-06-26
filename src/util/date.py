"""Dates for the project."""

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


def is_latest(year: int, month: int):
    return (year, month) in supported_dates()[-2:]
        
             
            
         