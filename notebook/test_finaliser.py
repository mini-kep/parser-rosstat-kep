import os
import tempfile

import pandas as pd
import pytest

from access import get_dataframe
from to_excel import to_xls


def test_get_dataframe():
    for freq in 'aqm':
        df = get_dataframe(freq)
        assert isinstance(df, pd.DataFrame)


def test_write_xls_writes_some_xlsx_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_filename = os.path.join(tmpdirname, '123.xlsx')
        df = pd.DataFrame()
        to_xls(temp_filename, df, df, df)        


if __name__ == "__main__":
    pytest.main([__file__])
