import pandas as pd


def get_duplicates(df):
    if df.empty:
        return df
    else:
        return df[df.duplicated(keep=False)]


def check_duplicates(df):
    dups = df[df.duplicated(keep=False)]
    if not dups.empty:
        # как писать не зкшет а warnings?
        # FIXME: issue warnings
        print("Warning: duplicate rows found:\n{}".format(dups))

# EP: можно еще как-то съедать список, чтобы при последующих просмотрах он был менше? 
def subset(values, freq):
    # WONTFIX: can also .pop()
    return [x for x in values if x['freq'] == freq]


def create_base_dataframe(datapoints, freq):
    df = pd.DataFrame(datapoints)
    if df.empty:
        raise ValueError(('Empty', datapoints))
    df = df[df.freq == freq]
    check_duplicates(df)
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

# EP: видимо нужно оставить одну какую-то функцию
def to_dataframes(datapoints):
    #datapoints = list(datapoints)
    return dict(a=create_dfa(datapoints),
                q=create_dfq(datapoints),
                m=create_dfm(datapoints)
                )

def unpack_dataframes(datapoints):
    #datapoints = list(datapoints)
    return [f(datapoints) for f in (create_dfa, create_dfq, create_dfm)] 


# TODO: bring back original tests
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


if __name__ == '__main__':
    import pathlib
    from reader import to_values
    from parsing_definition import NAMERS, UNITS
    from dev_helper import PATH
    filename = str(pathlib.Path(__file__).with_name('tab.csv'))
    values = to_values(PATH, UNITS, NAMERS)
    dfa, dfq, dfm = unpack_dataframes(values)
    dfs = to_dataframes(values)


# FIXME: must check why happens
"""Warning: duplicate rows found:
        date freq        label  value
8803  2016-5    m  PPI_mln_rub  101.4
8839  2016-2    m  PPI_mln_rub  101.1
8842  2016-5    m  PPI_mln_rub  101.4
8878  2016-2    m  PPI_mln_rub  101.1"""
