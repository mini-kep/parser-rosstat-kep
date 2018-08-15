import os
import tempfile

import pandas as pd
import pytest

from kep.dataframe.to_excel import save_excel


def test_write_xls_writes_some_xlsx_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, '123.xlsx')
        df = pd.DataFrame()
        save_excel(path, a=df, q=df, m=df)
        os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__])
