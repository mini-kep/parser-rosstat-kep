import pytest

from collections import OrderedDict as odict


# testing:
from kep.rows import get_year, is_year, Row, Rows

#TODO: test csv readers here

class Test_get_year():
    def test_get_year(self):
        assert get_year("19991)") == 1999
        assert get_year("1999") == 1999
        assert get_year("1812") is False
        assert get_year("2051") is False

class Test_is_year():                              
    def test_is_year(self):
        assert is_year("19991)") is True
        assert is_year("1999") is True
        assert is_year("Объем ВВП") is False

# FIXME:                             
#    def test_on_all_heads(self):
#        for s in self.all_heads():
#            year = get_year(s)
#            assert isinstance(year, int) or year is False
#
#    @staticmethod
#    def all_heads():
#        """Emit all heads for debugging get_year()"""
#        import files
#        import rows
#        csv_path = files.get_path_csv()
#        csv_dicts = rows.read_csv(csv_path)
#        for d in csv_dicts:
#            yield d.name

class Test_Row:
    
    def setup_method(self):
        self.row1 = Row(['Объем ВВП', '', '', '', ''])
        self.row2 = Row(["1991 1)", "4823", "901", "1102", "1373", "1447"])
        self.row3 = Row(['abcd', '1', '2'])

    def test_name_property(self):
        assert self.row1.name == 'Объем ВВП'
        assert self.row2.name == "1991 1)"
        
    def test_data_property(self):
        assert self.row1.data == ['', '', '', '']
        assert self.row2.data == ["4823", "901", "1102", "1373", "1447"]

    def test_len_method(self):
        assert self.row1.len() == 4
        assert self.row2.len() == 5

    def test_is_datarow(self):
        assert self.row1.is_datarow() is False
        assert self.row2.is_datarow() is True

    def test_startswith_returns_bool(self):
        assert self.row1.startswith("Объем \"ВВП\"") is True
        assert self.row2.startswith("Объем ВВП") is False
        # numbering is considered in Rows
        assert Row(["1.1 Объем ВВП"]).startswith("Объем ВВП") is False
                  
    def test_matches_returns_bool(self):
        assert self.row1.matches("Объем ВВП") is True
        assert self.row2.matches("Объем ВВП") is False
                                   
    def test_single_value(self):
        assert Row(['abcd', '1', '2']).__single_value__(['a']) == 'a'
        assert Row(['abcd', '1', '2']).__single_value__([]) is False
        with pytest.raises(ValueError):
            assert Row(['abcd', '1', '2']).__single_value__(['a', 'a'])                  
     
    def test_get_year(self):
        assert Row(["1999", "1", "2"]).get_year() == 1999   
    
    def test_get_varname(self):               
        assert Row(["1. abcd"]).get_varname({'1. ab':"ZZZ"}) == 'ZZZ'
        assert Row(["1. abcd"]).get_varname({'bc':"ZZZ"}) is False
        with pytest.raises(ValueError):
            assert Row(["1. abcd"]).get_varname({'1. ab':"ZZZ", '1. abcd':"YYY"}) 
    
    def test_get_unit(self):
        unit_mapper = odict([('%',"pct"), ('% change',"pct2")])
        assert Row(["1. abcd, % change"]).get_unit(unit_mapper) == 'pct'               
    
    def test_eq(self):
        class MockRow:
           name = "abcd"       
           data = ['1', '2']        
        r = MockRow
        assert Row(['abcd', '1', '2']).__eq__(r)

    def test_repr_method(self):        
        assert repr(self.row1) == "Row(['Объем ВВП', '', '', '', ''])"
        assert repr(self.row2) == "Row(['1991 1)', '4823', '901', '1102', '1373', '1447'])"    
    
    def test_str_method(self):        
        assert str(self.row1) == "<Объем ВВП>"
        assert str(self.row2) == "<1991 1) | 4823 901 1102 1373 1447>"
    
def mock_read_csv(_):
    yield Row(["apt", "1", "2"])
    yield Row(["bat aa...ah", "1", "2"])
    yield Row(["can", "1", "2"])
    yield Row(["dot oo...eh", "1", "2"])
    yield Row(["wed", "1", "2"])
    yield Row(["zed"])

@pytest.fixture
def rows():
    # 'dependency injection' by *reader_func* allows bypass
    # construction of mock csv file and use stream of Rows() directly,
    # this makes testing more modular and transparent
    return Rows(csv_path=None, reader_func=mock_read_csv)

class Test_Rows:
    
    def test_pop(self):
        # NOT TEST: fixture too complex, testing __pop_segment__() instead
        pass    

    def test_pop_segment_and_remaining_rows_behaviour(self, rows):    
        a = rows.__pop_segment__("bat", "dot")
        assert len(a) == 2      
        b = rows.__pop_segment__("apt", "wed")  
        assert len(b) == 2    
        c = rows.remaining_rows()
        assert c[0] == Row(['wed', '1', '2'])
        assert c[1] == Row(['zed'])
        
if __name__ == "__main__":
    pytest.main([__file__])