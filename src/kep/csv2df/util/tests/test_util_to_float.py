import pytest
from kep.csv2df.util_to_float import to_float
import pandas as pd

class Test_to_float:
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert to_float(x) is False

    def test_on_single_value_returns_float(self):
        assert to_float('5.678,') == 5.678
        assert to_float('5.678,,') == 5.678
        assert to_float("5.6") == 5.6
        assert to_float("5,6") == 5.6
        assert to_float("5,67") == 5.67
        assert to_float("5,67,") == 5.67

    def test_on_comments_returns_float(self):
        assert to_float('123,0 4561)') == 123
        assert to_float('6762,31)2)') == 6762.3
        assert to_float('1734.4 1788.42)') == 1734.4

    def test_on_max_recursion_depth_throws_exception(self):
        with pytest.raises(ValueError):
            to_float("1.2,,,,,")


