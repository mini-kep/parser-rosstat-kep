import pandas as pd
import warnings
from kep.util import timestamp

__all__ = ['unpack_dataframes']


def check_duplicates(df):
    dups = df[df.duplicated(keep=False)]
    if not dups.empty:
        warnings.warn("Duplicate rows found:\n{}".format(dups))


def subset(values, freq):
    return [x for x in values if x['freq'] == freq]


def make_timestamp(x):
    date = timestamp(x.year, x.month)
    return pd.Timestamp(date)


def separate_dataframes(datapoints):
    datapoints = list(datapoints)
    return [[d for d in datapoints if d.freq == freq] for freq in 'aqm']
        

def create_base_dataframe(datapoints, freq):
    df = pd.DataFrame(datapoints)
    if df.empty:
        raise ValueError(('Empty', datapoints))
    #df = df[df.freq == freq]
    check_duplicates(df)
    df = df.drop_duplicates(['freq', 'label', 'year', 'month'], keep='first')
    df['date'] = df.apply(make_timestamp, axis=1)
    # reshape
    df = df.pivot(columns='label', values='value', index='date')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    return df


def create_dfa(datapoints):
    df = create_base_dataframe(datapoints, 'a')
    return rename_accum(df)


def create_dfq(datapoints):
    df = create_base_dataframe(datapoints, 'q')
    df.insert(1, "qtr", df.index.quarter)
    return deaccumulate(df, first_month=3)


def create_dfm(datapoints):
    df = create_base_dataframe(datapoints, 'm')
    df.insert(1, "month", df.index.month)
    return deaccumulate(df, first_month=1)


def unpack_dataframes(datapoints):
    """Return a tuple of annual, quarterly, monthly pandas dataframes."""
    a, q, m = separate_dataframes(datapoints)    
    return create_dfa(a), create_dfq(q), create_dfm(m)


# TODO: need to be changed according to new format - must use 'a' as 'm12'
# government revenue and expense time series transformation


def rename_accum(df):
    return df.rename(mapper=lambda s: s.replace('_ACCUM', ''), axis=1)


def deacc_main(df, first_month):
    # save start of year values
    original_start_year_values = df[df.index.month == first_month].copy()
    # take a difference
    df = df.diff()
    # write back start of year values (January in monthly data, March in qtr
    # data)
    ix = original_start_year_values.index
    df.loc[ix, :] = original_start_year_values
    return df


def deaccumulate(df, first_month):
    varnames = [
        vn for vn in df.columns if vn.startswith('GOV') and (
            "ACCUM" in vn)]
    df[varnames] = deacc_main(df[varnames], first_month)
    return rename_accum(df)
