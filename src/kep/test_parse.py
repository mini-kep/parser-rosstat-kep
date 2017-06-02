# -*- coding: utf-8 -*-
import parse
import pytest

def test_end_to_end():
    parse.approve_csv(year=None,month=None)

def test_get_year():
    #FIXME: duplicates in cell.py
    assert parse.get_year("19991)") == 1999
    
if __name__ == "__main__":
    pytest.main()