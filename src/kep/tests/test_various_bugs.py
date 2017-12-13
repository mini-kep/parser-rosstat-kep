"""Regression tests / bug fixes on occasional errors."""

import pytest
from pathlib import Path
import pandas as pd
from io import StringIO

from ..config import find_repo_root, InterimCSV
from ..download.download import make_url


@pytest.mark.skip(
    "with new user import addressing index by 0 column, we do not need time_index")
def test_time_index_is_included_in_access():

    def make_path(freq):
        folder = find_repo_root() / 'data' / 'processed' / 'latest'
        return str(folder / "df{}.csv".format(freq))

    for freq in 'aqm':
        # a workaround for Windows problem
        # https://github.com/pandas-dev/pandas/issues/15086
        content = Path(make_path(freq)).read_text()
        filelike = StringIO(content)
        df = pd.read_csv(filelike)
        assert df.columns[0] == 'time_index'


def test_csv_has_no_null_byte():
    csv_path = InterimCSV(2015, 2).path
    z = csv_path.read_text(encoding='utf-8')
    assert "\0" not in z

# HS: add a test function for the make_url -- check that the formatting works
# FIXME: 'will_not_work_without_string_format' - does not explain what happens


def test_make_url_will_not_work_without_string_format():
    year = 2017
    month = 2
    url = make_url(year, month)
    assert '{' not in url


if __name__ == "__main__":
    pytest.main([__file__])
