import pytest

# testing:
from ..rows import get_year, is_year, Row

#TODO: move testing csv readers here

class Test_get_year_is_year():
    def test_get_year(self):
        assert get_year("19991)") == 1999
        assert get_year("1999") == 1999
        assert get_year("1812") is False
        assert get_year("2051") is False
                              
    def test_is_year(self):
        assert is_year("19991)") is True
        assert is_year("1999") is True
        assert is_year("Объем ВВП") is False
                             
    def test_on_all_heads(self):
        for s in self.all_heads():
            year = get_year(s)
            assert isinstance(year, int) or year is False

    @staticmethod
    def all_heads():
        """Emit all heads for debugging get_year()"""
        import files
        import rows
        csv_path = files.get_path_csv()
        csv_dicts = rows.read_csv(csv_path)
        for d in csv_dicts:
            yield d.name

class Test_Row:
    
    def setup_method(self):
        self.row1 = Row(['Объем ВВП', '', '', '', ''])
        self.row2 = Row(["1991 1)", "4823", "901", "1102", "1373", "1447"])

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
        assert self.row1.startswith("Объем ВВП") is True
        assert self.row2.startswith("Объем ВВП") is False
        # numbering is considered in Rows
        assert Row(["1.1 Объем ВВП"]).startswith("Объем ВВП") is False

    def test_repr_method(self):        
        assert repr(self.row1) == "Row ['Объем ВВП', '', '', '', '']"
        assert repr(self.row2) == "Row ['1991 1)', '4823', '901', '1102', '1373', '1447']"    
    
    def test_str_method(self):        
        assert str(self.row1) == "<Объем ВВП>"
        assert str(self.row2) == "<1991 1) | 4823 901 1102 1373 1447>"
    
if __name__ == "__main__":
    pytest.main([__file__])    