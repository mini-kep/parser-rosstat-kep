import random
from profilehooks import profile

from kep.extract import read_tables, parse_tables, get_datapoints, validate
from kep.dataframe import unpack_dataframes
from kep.parameters import ParsingParameters, CheckParameters
from kep.util.man import print_reference
from kep.util.locations import interim_csv
from kep.util.dates import date_span

ALL_DATES = date_span('2009-04', '2018-06')       

def random_date():
    return random.choice(ALL_DATES)

def random_dates(n):
    return [random_date() for _ in range(n)]

def extract_tables(year, month):
    p = ParsingParameters
    path = interim_csv(year, month)
    tables = read_tables(path)
    return parse_tables(tables, p.common_dicts, p.segment_dicts, p.units_dict) 

def get_dataframes(year, month):    
    tables = extract_tables(year, month)
    values = get_datapoints(tables)
    c = CheckParameters
    print_reference(tables, c.group_dict)
    validate(values, c.mandatory_list, c.optional_lists) 
    return unpack_dataframes(values)

def get_dataframe_dict(year, month):
    dfs = get_dataframes(year, month)
    return {freq: df for freq, df in zip('aqm', dfs)}

@profile(immediate=True, entries=20)
def run_sample(sample_size=3):
    """Run parsing for all dates and return latest set of tables."""
    for year, month in random_dates(sample_size):
        print(year, month)
        extract_tables(year, month)
        
if __name__ == '__main__':
    run_sample()
    year, month = 2018, 6 
    tables = extract_tables(year, month)
    dfa, dfq, dfm = get_dataframes(year, month)
    