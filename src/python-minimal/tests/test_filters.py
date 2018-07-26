from kep.filters import clean_year, clean_value, number_string

def test_number_string():
    assert number_string('-') == ""
    assert number_string('…') == ""    

def test_clean_year():
	assert clean_year('20052),3)') == 2005
	assert clean_year('20114)') == 2011
	assert clean_year('abc') is None
	assert clean_year('') is None
	assert clean_year('111') is None
	assert clean_year('1001') == 1001

def test_clean_value():
	assert clean_value('406911)') == 40691
	assert clean_value('211,32)') == 211.3