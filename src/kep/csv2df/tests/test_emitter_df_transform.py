import pytest
import pandas as pd
from pandas.util.testing import assert_frame_equal

from .shared import dfa, dfq, dfm
from ..emitter import (rename, select_varnames, deaccumulate_qtr, 
                       deaccumulate_month)

def make_df(data_dict):
    return pd.DataFrame(
        data=data_dict,
        index=pd.date_range(
            start="1999-01-01",
            periods=8,
            freq='Q'))

from itertools import accumulate
a = [10, 10, 10, 10]
b = [3, 3, 3, 3]
a1, b1 = (list(accumulate(x)) for x in (a, b))

dq = make_df({'VARNAME_bln': a + b})
dq_accum = make_df({'VARNAME_ACCUM_bln': a1 + b1})


def test_deaccumulate_qtr():
    deacc = deaccumulate_qtr(dq_accum)
    assert all(deacc - dq == 0)


# fixtures ?

#varnames = df_transform.select_varnames(dfm)
#gov_dfm = dfm[varnames]
#gov_dfq = dfq[varnames]
#last_month_values = gov_dfm[gov_dfm.index.month == 12]
#
#diff_dfm = df_transform.deaccumulate_month(gov_dfm)
#diff_dfq = df_transform.deaccumulate_qtr(gov_dfq)



# Code under test:

## government revenue and expense transformation
#
#
#def rename(df):
#    colname_mapper = {vn: vn.replace("_ACCUM", "") for vn in df.columns}
#    return df.rename(columns=colname_mapper)
#
#
#def select_varnames(df):
#    return [vn for vn in df.columns if vn.startswith('GOV') and "ACCUM" in vn]
#
#
#def deaccumulate_qtr(df):
#    return deaccumulate(df, first_month=3)
#
#
#def deaccumulate_month(df):
#    return deaccumulate(df, first_month=1)
#
#
#def deaccumulate(df_full, first_month):
#    varnames = select_varnames(df_full)
#    df = df_full[varnames]
#    # save start of year values
#    original_start_year_values = df[df.index.month == first_month].copy()
#    # take a difference
#    df = df.diff()
#    # write back start of year values
#    # (January in monthly data, March in qtr data)
#    ix = original_start_year_values.index
#    df.loc[ix, :] = original_start_year_values
#    # rounding
#    df = df.round(1)
#    # write back to original frame
#    df_full[varnames] = df
#    return rename(df_full)


### TODO: tests here

#class Test_Deaccumulated:
#    def test_monthly_diff_adds_to_annual(self):
#        """The deaccumulated GOV values in the monthly dataframe should add up
#            to the last month in the year in the annual dataframe.
#        """
#        assert_frame_equal(diff_dfm.resample('A').sum(),
#                           df_transform.rename(last_month_values))
#
#    def test_quarterly_diff_adds_to_annual(self):
#        """The deaccumulated GOV values in the quarterly dataframe should add
#            up to the last month in the year in the annual dataframe.
#        """
#        assert_frame_equal(diff_dfq.resample('A').sum(),
#                           df_transform.rename(last_month_values))
#
#    def test_monthly_diff_adds_to_quarterly_diff(self):
#        """The deaccumulated monthly dataframe aggregated to the quarter should
#            equal the deaccumulated quarterly dataframe.
#        """
#        assert_frame_equal(diff_dfm.resample('Q').sum(), diff_dfq)
#
#    def test_monthly_diff_adds_to_first_quarter(self):
#        """The deaccumulated GOV values in the monthly dataframe first quarter
#        end should add up to the first quarter end in the quarterly dataframe.
#        """
#        assert_frame_equal(diff_dfm.resample('Q').sum()[::4],  # every quarter
#                           df_transform.rename(gov_dfq[gov_dfq.index.month ==
#                                                       3]))


if __name__ == "__main__":
    pytest.main([__file__])
