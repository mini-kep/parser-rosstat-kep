import pytest
from collections import OrderedDict as odict
from pathlib import Path
from tempfile import NamedTemporaryFile


from ..reader import yield_csv_rows, to_rows, filter_csv_rows, open_csv
from ..reader import get_year, is_year, Row, RowStack

@pytest.fixture
def temp_path():
    with NamedTemporaryFile() as f:
        abspath = f.name
    p = Path(abspath)
    p.write_text("abc\n123")
    return p


class Test_open_csv:

    def test_on_string_argument_raises_TypeError(self):
        path_string = "abc.csv"
        with pytest.raises(TypeError):
            open_csv(path_string)

    def test_on_Path_runs_with_no_error(self, temp_path):
        assert open_csv(temp_path)

    def test_on_Path_provides_readable_input(self, temp_path):
        with open_csv(temp_path) as f:
            assert f.readlines() == ["abc\n", "123"]
