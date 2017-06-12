# -*- coding: utf-8 -*-
import pytest
import files

def test_InterimDataLocation():
    assert int(files.InterimDataLocation().max_year()) >= 2017
    mm = int(files.InterimDataLocation().max_month())
    assert mm <= 12 
    assert mm >= 1 
    
if __name__ == "__main__":
    pytest.main()