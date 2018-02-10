"""Dates for the project.

Constant:
    SUPPORTED_DATES

Method:
    assert_supported_date(), assert_latest_date()
"""

import pandas as pd


def supported_dates(start_date='2009-04', exclude_dates=['2013-11']):
    """Get a list of (year, month) tuples starting from (2009, 4) up to 
       a previous recent month. This a 'supported date list'.

       Excludes (2013, 11) - no archive for this month.
       
    Returns:
        List of (year, month) tuples.
    """
    end_date = pd.to_datetime('today') - pd.offsets.MonthEnd()
    dates = pd.date_range(start_date, end_date, freq='MS')
    exclude = map(pd.to_datetime, exclude_dates)
    return [(date.year, date.month) for date in dates.drop(exclude)]


class Date:
    
    supported_dates = supported_dates()
    random_valid_date = supported_dates[0]
    """
    Publication KEP for month x is released on end of month x+1 
    or start of month x+2. For more precise schedule see:
        <http://www.gks.ru/gis/images/graf-oper2018.htm>
    
    Assumption: we allow to look for latest date in last two recent months.       
    """
    latest_dates = supported_dates[-2:]

    def __init__(self, year: int, month: int):
        self.year, self.month = year, month
        
    def is_supported(self):
        return (self.year, self.month) in self.supported_dates

    def is_latest(self):    
        return (self.year, self.month) in self.latest_dates

#    @property
#    def latest(self):
#        return self.supported[-2:]

    def assert_supported(self):
        """Raise ValueError if date is not in supported list."""
        if not self.is_supported():
            raise ValueError(f'{self} is not a supported date.')    
    
    def assert_latest(self):
        """Raise ValueError if date is not recent."""    
        if not self.is_latest():
            msg = (f'Operation cannot be completed on date: {self}\n'
                   f'Use use newer date: {self.latest_dates}')
            raise ValueError(msg)
            
    def __repr__(self):
        return f'Date(year={self.year}, month={self.month})'
    
             
            
         