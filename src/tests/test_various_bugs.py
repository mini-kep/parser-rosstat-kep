"""Regression tests / bug fixes on occasional errors."""

import pytest
from pathlib import Path
import pandas as pd
from io import StringIO

# HS did: import the find_repo_root
from config import find_repo_root
#from config import PathHelper, find_repo_root
# HS did:
from download.download import make_url

ROOT = find_repo_root()


def test_time_index_is_included_in_access():

    def make_path(freq):
        folder = ROOT / 'data' / 'processed' / 'latest'
        return str(folder / "df{}.csv".format(freq))

    for freq in 'aqm':
        # a workaround for Windows problem
        # https://github.com/pandas-dev/pandas/issues/15086
        content = Path(make_path(freq)).read_text()
        filelike = StringIO(content)
        df = pd.read_csv(filelike)
        assert df.columns[0] == 'time_index'

# Hayk: Remove this, since uses the PathHelper module. Ask if it should be replaced in some way
#def test_csv_has_no_null_byte():
#    csv_path = PathHelper.locate_csv(2015, 2)
#    z = csv_path.read_text(encoding='utf-8')
#    assert "\0" not in z

# HS did: add a test function for the make_url -- check that the formatting works
def test_make_url():

    year = 2017
    month = 2
    url = make_url(year, month)
    if '{' in url or '}' in url:
        assert False


if __name__ == "__main__":
    pytest.main([__file__])
