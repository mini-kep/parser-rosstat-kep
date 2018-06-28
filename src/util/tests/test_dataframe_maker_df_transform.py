from itertools import accumulate
from random import randint

import pandas as pd
import pytest

from util.dataframe import deaccumulate


def _make_df(name, values, freq):
    return pd.DataFrame(
        data={name: values},
        index=pd.date_range(
            start="1999-01-01",
            periods=len(values),
            freq=freq))


def _rnd():
    return randint(1, 10)


def create_df(freq):
    n = dict(Q=4, M=12)[freq]
    a_list = [_rnd()] * n
    b_list = [_rnd()] * n
    diff_df = _make_df('GOV_VARNAME_bln', a_list + b_list, freq)
    a_list, b_list = (list(accumulate(x)) for x in (a_list, b_list))
    acc_df = _make_df('GOV_VARNAME_ACCUM_bln', a_list + b_list, freq)
    return diff_df, acc_df


@pytest.mark.parametrize("freq, start_month", [
    ("Q", 3),
    ("M", 1),
])
def test_deaccumulate_qtr_and_month(freq, start_month):
    # setup
    df_diff, df_acc = create_df(freq)
    # call
    result = deaccumulate(df_acc, start_month)
    # check
    assert (df_diff - result).sum().iloc[0] == 0


if __name__ == "__main__":
    pytest.main([__file__])
