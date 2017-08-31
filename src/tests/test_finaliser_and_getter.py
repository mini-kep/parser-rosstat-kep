import pytest
import tempfile
import os
import pandas as pd

from finaliser import to_xls
from getter import get_dataframe


def test_get_dataframe():
    for freq in 'aqm':
        df_ = get_dataframe(freq)
        assert isinstance(df_, pd.DataFrame)


def test_write_xls_writes_some_xlsx_file():
    fn = os.path.join(tempfile.gettempdir(), '123.xlsx')
    df = pd.DataFrame()
    to_xls(fn, df, df, df)
    os.remove(fn)


if __name__ == "__main__":
    pytest.main([__file__])
