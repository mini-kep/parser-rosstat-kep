"""Creating pandas dataframes."""

import pandas as pd
from util.label import make_label


def get_duplicates(df):
    if df.empty:
        return df
    else:
        return df[df.duplicated(keep=False)]


def check_duplicates(df):
    if df.empty:
        dups = df
    else:
        dups = df[df.duplicated(keep=False)]
    if not dups.empty:
        # raise ValueError("Duplicate rows found {}".format(dups))
        print("Warning: duplicate rows found:\n{}".format(dups))


def convert_labels(x):
    varname = x['label'][0]
    unit = x['label'][1]
    z = dict(value=x['value'],
             freq=x['freq'],
             time_index=x['time_index'])
    z['label'] = make_label(varname, unit)
    return z


def convert_labels2(x):
    varname = x['label'][0]
    unit = x['label'][1]
    return x['freq'], x['value'], x['time_index'], make_label(varname, unit)


def to_dataframes(datapoints):
    dfs = split_to_freq(datapoints)
    for f in dfs.keys():
        dfs[f] = create_dataframe2(dfs[f], f)
    return dfs


def split_to_freq(gen):
    lists = {f: [] for f in 'aqm'}
    for x in gen:
        f = x['freq']
        lists[f].append(convert_labels(x))
    return lists


def make_base_dataframe(datapoints):
    datapoints = [convert_labels(x) for x in datapoints]
    df = pd.DataFrame(datapoints)
    df['label'] = df.apply(
        lambda df: df['label'][0] +
        '_' +
        df['label'][1],
        axis=1)
    if df.empty:
        return pd.DataFrame()
    check_duplicates(df)
    df = df.drop_duplicates(['freq', 'label', 'time_index'], keep='first')
    return df


def create_dataframe3(datapoints, freq):
    df = pd.DataFrame(datapoints)
    if df.empty:
        return pd.DataFrame()
    check_duplicates(df)
    df = df.drop_duplicates(['freq', 'label', 'time_index'], keep='first')
    # reshape
    df = df.pivot(columns='label', values='value', index='time_index')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    # add period
    if freq == "q":
        df.insert(1, "qtr", df.index.quarter)
    if freq == "m":
        df.insert(1, "month", df.index.month)
    # transform variables:
    if freq == "a":
        df = rename_accum(df)
    if freq == "q":
        df = deaccumulate(df, first_month=3)
    if freq == "m":
        df = deaccumulate(df, first_month=1)
    return df


def create_dataframe2(base_df, freq):
    df = base_df[base_df.freq == freq]
    # reshape
    df = df.pivot(columns='label', values='value', index='time_index')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    # add period
    if freq == "q":
        df.insert(1, "qtr", df.index.quarter)
        df = deaccumulate(df, first_month=3)
    if freq == "m":
        df.insert(1, "month", df.index.month)
        df = deaccumulate(df, first_month=1)
    if freq == "a":
        df = rename_accum(df)
    return df


def create_dataframe(datapoints, freq):
    df = pd.DataFrame([x for x in map(convert_labels, datapoints)
                       if x['freq'] == freq])
    if df.empty:
        return pd.DataFrame()
    check_duplicates(df)
    df = df.drop_duplicates(['freq', 'label', 'time_index'], keep='first')
    # reshape
    df = df.pivot(columns='label', values='value', index='time_index')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    # add period
    if freq == "q":
        df.insert(1, "qtr", df.index.quarter)
    if freq == "m":
        df.insert(1, "month", df.index.month)
    # transform variables:
    if freq == "a":
        df = rename_accum(df)
    if freq == "q":
        df = deaccumulate(df, first_month=3)
    if freq == "m":
        df = deaccumulate(df, first_month=1)
    return df


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
