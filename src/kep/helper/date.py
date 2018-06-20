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


class Date:    
    """
    Publication KEP for month x is released on end of month x+1 
    or start of month x+2. 
    
    For more precise schedule see:
        <http://www.gks.ru/gis/images/graf-oper2018.htm>
    """

    supported_dates = supported_dates()
    
    def __init__(self, year: int, month: int):
        if (year, month) not in self.supported_dates:
            raise ValueError(f'Date not supported: {year}-{month}')
        self.year, self.month = year, month        

    def is_latest(self):
        return (self.year, self.month) in self.supported_dates[-2:]
        
    def __repr__(self):
        return f'Date(year={self.year}, month={self.month})'
    
             
            
         