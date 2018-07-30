import calendar

MONTHS = dict(a=12, q=3, m=1)

def timestamp(freq: str, 
              year: str, 
              period: int):
    year = filters.clean_year(year)
    month = MONTHS[freq] * period
    day = calendar.monthrange(year, month)[1]
    return f'{year}-{str(month).zfill(2)}-{day}'
    
def timestamp_short(freq: str, 
                    year: str, 
                    period: int):
    if freq == 'a':
        return year
    if freq == 'q':
        period = period * 3
    month = str(period).zfill(2)
    return f'{year}-{month}'
