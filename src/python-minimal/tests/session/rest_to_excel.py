import os
import tempfile

import pandas as pd
import pytest

from util.to_excel import save_excel


def test_write_xls_writes_some_xlsx_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_filename = os.path.join(tmpdir, '123.xlsx')
        df = pd.DataFrame()
        save_excel(temp_filename, dict(a=df, q=df, m=df))


if __name__ == "__main__":
    pytest.main([__file__])
