# -*- coding: utf-8 -*-
import parse
import cfg
import pytest

def test_end_to_end():
    parse.approve_csv(year=None,month=None)


def test_end_to_end_many_dates():
    # needs cleaner data directory, will fail on incomplete files
    pts = [{'freq': 'a', 'label': 'GDP__bln_rub', 'value': 4823.0, 'year': 1999}]
    # FIXME approve_all too slow - suite runs for 7.9 sec! even with one control value
    #       one control value as above, 19.68 sec with creating dataframes.
    parse.approve_all(valid_datapoints=pts)

def test_get_year():
    assert parse.get_year("19991)") == 1999
    
    
def test_csv_has_no_null_byte():     
    csv_path = cfg.get_path_csv(2015, 2) 
    z = csv_path.read_text(encoding = parse.ENC)    
    assert "\0" not in z
    
    
if __name__ == "__main__":
    pytest.main()