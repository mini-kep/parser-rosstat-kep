# -*- coding: utf-8 -*-
import pytest
import datetime as dt
import pandas as pd
from getter import get_dataframe


def test_get_dataframe():
    for freq in 'aqm':
        df_ = get_dataframe(freq)
        assert isinstance(df_, pd.DataFrame)





if __name__ == "__main__":
    pytest.main([__file__])
