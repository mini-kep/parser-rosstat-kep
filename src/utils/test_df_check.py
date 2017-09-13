# -*- coding: utf-8 -*-
import pytest
import pandas as pd

import df_check

# input
dq1 = pd.DataFrame(
    data=dict(
        X_bln=[
            10, 10, 10, 10]), index=pd.date_range(
                start="1999-01-01", periods=4, freq='Q'))
da1 = pd.DataFrame(data=dict(X_bln=[40]),
                   index=[pd.to_datetime("1999") + pd.offsets.YearEnd()])


def test_levels():
    assert df_check.aggregate_levels_to_annual(dq1).equals(da1)


# input
dq2 = pd.DataFrame(
    data=dict(
        X_rog=[
            100,
            100,
            100,
            100,
            102.5,
            100,
            100,
            100,
        ]),
    index=pd.date_range(
        start="1999-01-01",
        periods=8,
        freq='Q'))
da2 = pd.DataFrame(data=dict(X_yoy=[102.5]),
                   index=[pd.to_datetime("2000") + pd.offsets.YearEnd()])


def test_avg_rates():
    assert all(df_check.aggregate_rates_to_annual_average(dq2) - da2 < 0.01)


if __name__ == "__main__":
    pytest.main([__file__])
