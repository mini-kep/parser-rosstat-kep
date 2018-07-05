#EP: может переименовать этот файл?

import pathlib
from parsing_definition import NAMERS, UNITS
from reader import to_values
from saver import to_dataframes
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


def run_df():
    x = run_to_values()
    to_dataframes(x)


def foo(x, freq):
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


def run_foo():
    x = run_to_values()
    foo(x, 'm')


def run_bare_df():
    x = run_to_values()
    df = pd.DataFrame(x)
    df = df[df.freq == 'm']


def tester(code: str):
    n = 5
    msec = 1000 / n * timeit(code, 'import dev_helper', number=n)
    return round(msec, 1)


if __name__ == '__main__':
    print('Get datapoints', tester(
        'dev_helper.to_values(dev_helper.PATH, dev_helper.UNITS, dev_helper.NAMERS)'))
    print('Bare dataframe', tester('dev_helper.run_bare_df()'))
    print('Decorated dataframe', tester('dev_helper.run_foo()'))
    # TODO: channel warnings away from stdout
    # EP: почему создание трех фреймов выполняется быстрее чем одного?
    print('All dataframes', tester('dev_helper.run_df()'))
