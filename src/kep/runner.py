"""Access interim CSV file by year and month, parse values, validate and create pandas dataframes by frequency."""
import random
from profilehooks import profile

from kep.engine import read_tables, parse_tables, datapoints, validate
from kep.dataframe import unpack_dataframes
from kep.parameters import ParsingParameters, CheckParameters
from kep.utilities.synopsis import print_reference
from kep.utilities.locations import interim_csv
from kep.utilities.dates import date_span

__all__ = ['get_dataframes', 'get_dataframe_dict', 'run_sample']


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
    """
    Return a tuple of annual, quarterly and monthly dataframes by *year* and *month*.
    Prints parsing synopsis to stdout. 
    """
    tables = extract_tables(year, month)
    values = datapoints(tables)
    c = CheckParameters
    print_reference(tables, c.group_dict)
    validate(values, c.mandatory_list, c.optional_lists) 
    return unpack_dataframes(values)


def get_dataframe_dict(year, month):
    """Return a dictionary with annual, quarterly and monthly dataframes by *year* and *month*."""
    _dataframes = get_dataframes(year, month)
    return {freq: df for freq, df in zip('aqm', _dataframes)}


@profile(immediate=True, entries=20)
def run_sample(n=3):
    """Run parsing for *n* random historic dates."""
    for year, month in random_dates(n):
        print(year, month)
        extract_tables(year, month)


if __name__ == '__main__':
    run_sample()
    year, month = 2018, 6 
    tables = extract_tables(year, month)
    dfa, dfq, dfm = get_dataframes(year, month)