#EP: может переименовать этот файл?

import pathlib
from parsing_definition import NAMERS, UNITS
from reader import to_values
from saver import to_dataframes, create_base_dataframe
import pandas as pd
from timeit import timeit

datafolder = pathlib.Path(__file__).parent / 'data'
PATH = str(datafolder / 'tab.csv')
PATH_LEGACY = str(datafolder / 'tab_old.csv')


def messup(values):
    messed_years = set()
    messed_values = set()
    for v in to_values(PATH, UNITS, NAMERS):
        year = v['year']
        value = v['value'].replace(',', '.').replace('…', '')
        try:
            assert int(year) <= 2018 and int(year) >= 1998
        except BaseException:
            messed_years.add(year)
        try:
            float(value) if value else 0
        except BaseException:
            messed_values.add(value)
    return messed_years, messed_values


def run_to_values():
    return to_values(PATH, UNITS, NAMERS)

def run_bare_df():
    x = run_to_values()
    df = pd.DataFrame(x)
    df = df[df.freq == 'm']


def create_df(x, freq):
    x = run_to_values()
    df = pd.DataFrame(x)
    df = df[df.freq == freq]
    # check_duplicates(df)
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

def run_create_dataframe():
    x = run_to_values()
    create_base_dataframe(x, 'm')
    
def run_df():
    x = run_to_values()
    to_dataframes(x)
    




def tester(code: str):
    n = 5
    module = 'dev_timer'
    msec = 1000 / n * timeit(code, f'import {module}', number=n)
    return round(msec, 1)


def timer():
    print('Exеcution time in millisecond')
    for i, (msg, x) in enumerate([
            
         ('Get datapoints as list', 
          'dev_timer.run_to_values()')
         
        ,('Bare dataframe', 
          'dev_timer.run_bare_df()')
        
        ,('Decorated dataframe (create_df)', 
          "dev_timer.create_df(x=dev_timer.run_to_values(), freq='m')")
        
        ,('Decorated dataframe (saver.create_base_dataframe)', 
          'dev_timer.run_create_dataframe()')

        ,('3 dataframes (saver.create_base_dataframe)', 
          'dev_timer.run_df()')

        ]):
        print(f'{i+1})', msg, tester(x))

def replicate_dupl_error():
    values = to_values(PATH, UNITS, NAMERS)
    df = pd.DataFrame(values)
    dups = df[df.duplicated(keep=False)]
    print(dups)
    return dups   

#TODO: how to control warnings 
#import warnings
#warnings.simplefilter("error")

if __name__ == '__main__':
    #timer()
    replicate_dupl_error()
