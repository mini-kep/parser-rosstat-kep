import pytest
import pandas as pd
from itertools import accumulate
from random import randint

from kep.csv2df.emitter import deaccumulate_qtr, deaccumulate_month


def _make_df(name, values, freq):
    return pd.DataFrame(
        data={name: values},
        index=pd.date_range(
            start="1999-01-01",
            periods=len(values),
            freq=freq))

def _rnd():
    return randint(1,10)

def create_df(freq):
    n = dict(Q=4, M=12)[freq]
    a_list = [_rnd()] * n
    b_list = [_rnd()] * n
    diff_df = _make_df('GOV_VARNAME_bln', a_list + b_list, freq)
    a_list, b_list = (list(accumulate(x)) for x in (a_list, b_list))    
    acc_df = _make_df('GOV_VARNAME_ACCUM_bln', a_list + b_list, freq)
    return diff_df, acc_df

@pytest.mark.parametrize("freq, defunc", [
    ("Q", deaccumulate_qtr),
    ("M", deaccumulate_month),
]) 
def test_deaccumulate_qtr_and_month(freq, defunc):
    #setup
    df_diff, df_acc = create_df(freq)
    # call
    result = defunc(df_acc)
    # check
    assert (df_diff - result).sum().iloc[0] == 0

# TODO: use more tests

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
