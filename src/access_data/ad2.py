"""Read pandas dataframes from stable URL or local CSV files."""

#IDEA: make a check where monthly data is used to generate qtr and annual values

import pandas as pd

FREQUENCIES = "aqm" # or "aqmwd" for other datasets

def read_csv(source):
    """Canonical wrapper for pd.read_csv.
       Converts 'time_index' column to date format.
    """
    return pd.read_csv(source, converters={'time_index': pd.to_datetime},
                       index_col='time_index')
#test code
from io import StringIO
_source = StringIO("""time_index,EXPORT_GOODS_TOTAL_bln_usd,GDP_bln_rub
1999-12-31,75.6,4823.0""")
df = read_csv(source=_source) 
assert df.EXPORT_GOODS_TOTAL_bln_usd['1999-12-31'] == 75.6
assert df.GDP_bln_rub['1999-12-31'] == 4823.0

def validate_frequency(freq):
    if freq not in FREQUENCIES:
        raise ValueError("frequency <{}> must be in {}".format(freq, FREQUENCIES))        
                     
def get_url(freq):
    """Make URL for CSV files at different *freq*.
    """
    validate_frequency(freq)
    return "https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/" + \
           "data/processed/latest/df{}.csv".format(freq)

#test code
assert get_url("a") == 'https://raw.githubusercontent.com/epogrebnyak/mini-kep/master/data/processed/latest/dfa.csv'
assert get_url("q").endswith('dfq.csv')
assert get_url("m").endswith('dfm.csv')

def get_path(freq):
    """Make URL for CSV files at different *freq*.
    """
    validate_frequency(freq)
    # FIXME: save to temp folder, not saveing to project folder
    return "df{}.csv".format(freq)

def update():
    """Get CSV from web and save to local file.
    """
    for freq in "aqm":
        df = read_csv(get_url(freq))
        df.to_csv(get_path(freq))
        
def load():    
    """Load CSv from local files.
    """    
    dfs = {}
    for freq in "aqm":
        dfs[freq] = read_csv(get_path(freq))
    return dfs    
    
def get_dataframes():
    """Get three dataframes from local csv files.
    """
    try:
        dfs = load()
    except FileNotFoundError:
        update()
        dfs = load()
    return dfs['a'], dfs['q'], dfs['m']

if __name__ == "__main__":
    dfa, dfq, dfm = get_dataframes()
