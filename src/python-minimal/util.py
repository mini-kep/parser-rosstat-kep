import pathlib
from parsing_definition import NAMERS, UNITS
from reader import to_values
from saver import to_dataframes, create_base_dataframe 
import pandas as pd

PATH = str(pathlib.Path(__file__).with_name('tab.csv'))

def messup(values):                  
    messed_years = set()
    messed_values = set()
    for v in to_values(PATH, UNITS, NAMERS):
        year = v['year']
        value = v['value'].replace(',', '.').replace('…','')
        try:
            assert int(year) <= 2018 and int(year) >= 1998
        except:    
            messed_years.add(year)
        try: 
            float(value) if value else 0
        except:         
            messed_values.add(value)
    return  messed_years, messed_values       

x = list(to_values(PATH, UNITS, NAMERS))

def run_to_values():
     return list(to_values(PATH, UNITS, NAMERS))

def run_df():
    return to_dataframes(x) 

z = list({'freq': 'm'} for _ in range(10000))

def foo(x, freq):
    df = pd.DataFrame(x)
    df = df[df.freq == freq]
    #check_duplicates(df)
    df = df.drop_duplicates(['freq', 'label', 'date'], keep='first')
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
    # reshape
    df = df.pivot(columns='label', values='value', index='date')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    return df

def run_df1():
    foo(x, 'm')

def run_df3():
    df = pd.DataFrame(x)
    df = df[df.freq == 'm']


if __name__ == '__main__':
    from timeit import timeit
    n = 5
    # TODO: time to beat is benchmark time *t0*
    t1 = 1000 / n * timeit('run_df1()', 'from util import run_df1', number=n)
    t3 = 1000 / n * timeit('run_df3()', 'from util import run_df3', number=n)
    print(t1, t3)
    

