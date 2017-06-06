# -*- coding: utf-8 -*-
import pytest
import cfg

def test_InterimDataLocation():
    assert int(cfg.InterimDataLocation().max_year()) >= 2017
    mm = int(cfg.InterimDataLocation().max_month())
    assert mm <= 12 
    assert mm >= 1 
    
if __name__ == "__main__":
    pytest.main(__file__)