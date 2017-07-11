# -*- coding: utf-8 -*-
import pytest
from .. import files


def test_InterimDataFolder():
    assert int(files.InterimDataFolder().max_year()) >= 2017
    mm = int(files.InterimDataFolder().max_month())
    assert mm <= 12
    assert mm >= 1


if __name__ == "__main__":
    pytest.main()
