# -*- coding: utf-8 -*-
from pandas.util.testing import assert_frame_equal

# Issue: <https://github.com/epogrebnyak/mini-kep/issues/66>

# *gov_vars* variables accumulate from the start of the year
# need to take a difference and produce new variables with monthly and
# quarterly values


def select_varnames(df):
    return [vn for vn in df.columns if vn.startswith('GOV') and "ACCUM" in vn]


def rename(df):
    colname_mapper = {vn: vn.replace("_ACCUM", "") for vn in df.columns}
    return df.rename(columns=colname_mapper)


def deaccumulate_qtr(df):
    return deaccumulate(df, first_month=3)


def deaccumulate_month(df):
    return deaccumulate(df, first_month=1)


def deaccumulate(df, first_month):
    # first_month is 1 for dfm, 3 for dfq
    assert first_month in [1, 3]
    # save start of year values
    original_start_year_values = df[df.index.month == first_month].copy()
    # take a difference
    df = df.diff()
    # write back start of year values (January in monthly data,
    # March in qtr data)
    ix = original_start_year_values.index
    df.loc[ix, :] = original_start_year_values
    return rename(df)


if __name__ == '__main__':
    from df_values import dfa, dfm, dfq

    varnames = [vn for vn in dfa.columns
                if vn.startswith('GOV') and "ACCUM" in vn]

    # checking varnames
    assert select_varnames(dfm) == select_varnames(dfq)
    assert select_varnames(dfm) == select_varnames(dfa)

    # transformation of dfa, dfm, dfq
    gov_dfm = dfm[varnames]
    gov_dfq = dfq[varnames]
    gov_dfa = dfa[varnames]
    diff_dfm = deaccumulate_month(gov_dfm)
    diff_dfq = deaccumulate_month(gov_dfq)
    diff_dfa = rename(gov_dfa)

    # check 1
    last_month_values = gov_dfm[gov_dfm.index.month == 12]
    assert_frame_equal(diff_dfm.resample('A').sum(), rename(last_month_values))
