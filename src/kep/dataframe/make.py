import calendar
import pandas as pd

__all__ = ['unpack_dataframes']


# -----------------------------------------------------------------------------

def last_day(year: int, month: int) -> int:
    """Get a number like 28, 29, 30 or 31."""
    return calendar.monthrange(year, month)[1]


def timestamp(year: int, month: int) -> str:
    """Make end of month YYYY-MM-DD timestamp."""

    day = last_day(year, month)
    month = str(month).zfill(2)
    return f'{year}-{month}-{day}'


def make_timestamp(x):
    date = timestamp(x.year, x.month)
    try:
        return pd.Timestamp(date)
    except ValueError:
        raise ValueError(date)

# -----------------------------------------------------------------------------


# df = df.drop_duplicates(['freq', 'label', 'year', 'month'], keep='first')
def check_duplicates(df):
    dups = df[df.duplicated(keep=False)]
    if not dups.empty:
        raise ValueError("Duplicate rows found:", dups)


def check_empty(df):
    if df.empty:
        raise ValueError('Empty', df)


def create_base_dataframe(datapoints, freq):
    df = pd.DataFrame(datapoints)
    check_empty(df)
    check_duplicates(df)
    # create date
    df['date'] = df.apply(make_timestamp, axis=1)
    # reshape
    df = df.pivot(columns='label', values='value', index='date')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    return df

# -----------------------------------------------------------------------------


def subset(values, freq):
    return [x for x in values if x.freq == freq]


def separate_dataframes(datapoints, frequencies='aqm'):
    datapoints = list(datapoints)
    return [subset(datapoints, freq) for freq in frequencies]


def unpack_dataframes(datapoints):
    """Return a tuple of annual, quarterly, monthly pandas dataframes."""
    a, q, m = separate_dataframes(datapoints, frequencies='aqm')
    return create_annual(a), create_quarterly(q), create_monthly(m)


def create_annual(datapoints):
    df = create_base_dataframe(datapoints, 'a')
    return rename_accum(df)


def create_quarterly(datapoints):
    df = create_base_dataframe(datapoints, 'q')
    df.insert(1, "qtr", df.index.quarter)
    return deaccumulate(df, first_month=3)


def create_monthly(datapoints):
    df = create_base_dataframe(datapoints, 'm')
    df.insert(1, "month", df.index.month)
    return deaccumulate(df, first_month=1)


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
