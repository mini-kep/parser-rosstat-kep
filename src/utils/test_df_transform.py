# -*- coding: utf-8 -*-
import pytest
from pandas.util.testing import assert_frame_equal
import df_transform

from df_values import dfq, dfm

varnames = df_transform.select_varnames(dfm)
gov_dfm = dfm[varnames]
gov_dfq = dfq[varnames]
last_month_values = gov_dfm[gov_dfm.index.month == 12]

diff_dfm = df_transform.deaccumulate_month(gov_dfm)
diff_dfq = df_transform.deaccumulate_qtr(gov_dfq)

class Deaccumulated:
    def test_monthly_diff_adds_to_annual(self):
        """The deaccumulated GOV values in the monthly dataframe should add up
            to the last month in the year in the annual dataframe.
        """
        assert_frame_equal(diff_dfm.resample('A').sum(), last_month_values)

    def test_quarterly_diff_adds_to_annual(self):
        """The deaccumulated GOV values in the quarterly dataframe should add
            up to the last month in the year in the annual dataframe.
        """
        assert_frame_equal(diff_dfq.resample('A').sum(), last_month_values)

    def test_monthly_diff_adds_to_quarterly_diff(self):
        """The deaccumulated monthly dataframe aggregated to the quarter should
            equal the deaccumulated quarterly dataframe.
        """
        assert_frame_equal(diff_dfm.resample('Q').sum(), diff_dfq)

    def test_monthly_diff_adds_to_first_quarter(self):
        """The deaccumulated GOV values in the monthly dataframe first quarter
        end should add up to the first quarter end in the quarterly dataframe.
        """
        assert_frame_equal(diff_dfm.resample('Q').sum()[::4],  # every quarter
                           gov_dfq[gov_dfq.index.month == 3])
        

if __name__ == "__main__":
    pytest.main([__file__])
