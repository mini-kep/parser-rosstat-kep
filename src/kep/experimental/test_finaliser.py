import os
import tempfile

import pandas as pd
import pytest

from kep.experimental.finaliser import to_xls
from kep.experimental.getter import get_dataframe


def test_get_dataframe():
    for freq in 'aqm':
        df_ = get_dataframe(freq)
        assert isinstance(df_, pd.DataFrame)


def test_write_xls_writes_some_xlsx_file():
    temp_filename = os.path.join(tempfile.gettempdir(), '123.xlsx')
    df = pd.DataFrame()
    to_xls(temp_filename, df, df, df)
    os.remove(temp_filename)


if __name__ == "__main__":
    pytest.main([__file__])
