import pytest
from collections import OrderedDict as odict

from kep.csv2df.row_model import get_year, is_year, Row

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


class Test_Row:
    def setup_method(self):
        self.row1 = Row(["Объем ВВП", "", "", "", ""])
        self.row2 = Row(["1991 1)", "4823", "901", "1102", "1373", "1447"])
        self.row3 = Row(["abcd", "1", "2"])


class Test_Row_Attributes(Test_Row):

    def test_name_property_is_string(self):
        assert self.row1.name == "Объем ВВП"
        assert self.row2.name == "1991 1)"
        assert self.row3.name == "abcd"

    def test_data_property_is_list(self):
        assert self.row1.data == ["", "", "", ""]
        assert self.row2.data == ["4823", "901", "1102", "1373", "1447"]
        assert self.row3.data == ["1", "2"]


class Test_Row_Methods(Test_Row):

    def test_len_method_returns_int(self):
        assert len(self.row1) == 4
        assert len(self.row2) == 5
        assert len(self.row3) == 2

    def test_is_datarow_returns_bool(self):
        assert self.row1.is_datarow() is False
        assert self.row2.is_datarow() is True
        assert self.row3.is_datarow() is False

    def test_eq_compares_name_and_data_attributes(self):
        class MockRow:
            name = "abcd"
            data = ["1", "2"]
        r = MockRow
        assert Row(["abcd", "1", "2"]).__eq__(r)

    def test_repr_method(self):
        assert repr(self.row1) == "Row(['Объем ВВП', '', '', '', ''])"
        for row in [self.row1, self.row2, self.row3]:
            assert eval(repr(row)) == row

    def test_str_method(self):
        assert str(self.row1).startswith("<Объем ВВП")
        assert str(self.row2) == "<1991 1) | 4823 901 1102 1373 1447>"
        assert str(self.row3)  # just checking it is callable


class Test_Row_Methods_Used_for_Matching_Strings(Test_Row):

    def test_startswith_returns_bool(self):
        assert self.row1.startswith("Объем ВВП") is True
        assert self.row2.startswith("Объем ВВП") is False
        assert self.row1.startswith("ВВП") is False
        assert Row(["1.1 Объем ВВП"]).startswith("Объем ВВП") is False

    def test_startswith_ignores_apostrophe(self):
        assert self.row1.startswith('Объем \"ВВП\"') is True

    def test_matches_returns_bool(self):
        assert self.row1.matches("Объем ВВП") is True
        assert self.row2.matches("Объем ВВП") is False
        assert self.row1.matches("ВВП") is True

    def test_mathches_vs_startswith(self):
        row = Row(["many words in my head", "", "", ""])
        # any matching word is ok for Row.matches()
        # Row.startswith() only tests beginning of *Row.name*
        assert row.matches("words") is True
        assert row.startswith("words") is False


class Test_Row_get_varname(Test_Row):

    def test_finds_one_varname(self):
        assert Row(["1. abcd"]).get_varname({"ab": "ZZZ"}) == "ZZZ"

    def test_on_letters_inside_word_finds_nothing(self):
        # will not find anything, becase 'bc' is in the middle of string
        assert Row(["1. abcd"]).get_varname({"bc": "ZZZ"}) is False

    def test_on_similar_mapper_keys_finds_too_many_and_raises_error(self):
        # finds too many entries, raises error
        with pytest.raises(ValueError):
            varname_mapper_dict = {"abc": "ZZZ", "1. ab": "YYY"}
            assert Row(["1. abcd"]).get_varname(varname_mapper_dict)


class Test_Row_get_unit(Test_Row):

    def test_finds_one_unit(self):
        unit_mapper = {"%": "pct"}
        assert Row(["Rate, %"]).get_unit(unit_mapper) == "pct"

    def test_get_unit_uses_first_entry_in_unit_mapper_oredered_dict(self):
        unit_mapper = odict([("% change", "rog"), ("%", "pct")])
        assert Row(["1. abcd, % change"]).get_unit(unit_mapper) == "rog"
        assert Row(["1. abcd, % change"]).get_unit(unit_mapper) != "pct"


if __name__ == "__main__":
    pytest.main([__file__])
