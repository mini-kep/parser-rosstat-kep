import pytest

from namelist import NAMES, make_namelist

def test_make_namelist_on_asterisk_retuRns_expected_list_of_strings():
    result = make_namelist(patterns=['WAGE_*'], names=NAMES) 
    assert result == ['WAGE_NOMINAL_rub', 'WAGE_REAL_rog', 'WAGE_REAL_yoy']

def test_make_namelist_returns_sorted_list():
    names = ['WAGE_Z', 'WAGE_A']
    result = make_namelist(patterns=['WAGE_*'], names=names) 
    assert result == ['WAGE_A', 'WAGE_Z']
    
def test_make_namelist_on_string_returns_expected_list_of_names():
    result = make_namelist(patterns=['UNEMPL'], names=NAMES) 
    assert result == ['UNEMPL_pct']

def test_make_namelist_misses_name_in_the_middle():
    result = make_namelist(patterns=['WAGE_*'], names=['UNNECESSARY_WAGE_1']) 
    assert result == []

def test_make_namelist_misses_missing_string():
    result = make_namelist(patterns="ABC", names=['DEF', 'XYZ'])
    assert result == []

def test_make_namelist_ignores_lowercase_pattern():
    result = make_namelist(patterns="def", names=['DEF', 'XYZ'])
    assert result == []    

def test_make_namelist_ignores_lowercase_name():
    result = make_namelist(patterns="def", names=['def', 'XYZ'])
    assert result == []     
    
if __name__ == '__main__':
    pytest.main([__file__])    