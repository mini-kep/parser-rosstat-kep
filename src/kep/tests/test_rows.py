import pytest
from collections import OrderedDict as odict

from kep.rows import get_year, is_year, Row, RowStack

# TODO: test csv readers here


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
        self.row1 = Row(['Объем ВВП', '', '', '', ''])
        self.row2 = Row(["1991 1)", "4823", "901", "1102", "1373", "1447"])
        self.row3 = Row(['abcd', '1', '2'])

    def test_name_property(self):
        assert self.row1.name == 'Объем ВВП'
        assert self.row2.name == "1991 1)"
        assert self.row3.name == 'abcd'

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
        assert Row(["1.1 Объем ВВП"]).startswith("Объем ВВП") is False

    def test_matches_returns_bool(self):
        assert self.row1.matches("Объем ВВП") is True
        assert self.row2.matches("Объем ВВП") is False

    def test_get_year(self):
        assert Row(["1999", "1", "2"]).get_year() == 1999

    def test_get_varname(self):
        # finds one
        assert Row(["1. abcd"]).get_varname({'1. ab': "ZZZ"}) == 'ZZZ'
        # will not find anything
        assert Row(["1. abcd"]).get_varname({'bc': "ZZZ"}) is False
        # finds too many
        with pytest.raises(ValueError):
            assert Row(["1. abcd"]).get_varname(
                {'1. ab': "ZZZ", '1. abcd': "YYY"})

    def test_get_unit(self):
        unit_mapper = odict([('%', "pct"), ('% change', "pct2")])
        assert Row(["1. abcd, % change"]).get_unit(unit_mapper) == 'pct'

    def test_eq(self):
        class MockRow:
            name = "abcd"
            data = ['1', '2']
        r = MockRow
        assert Row(['abcd', '1', '2']).__eq__(r)

    def test_repr_method(self):
        assert repr(self.row1) == "Row(['Объем ВВП', '', '', '', ''])"
        assert repr(
            self.row2) == "Row(['1991 1)', '4823', '901', '1102', '1373', '1447'])"

    def test_str_method(self):
        assert str(self.row1) == "<Объем ВВП>"
        assert str(self.row2) == "<1991 1) | 4823 901 1102 1373 1447>"


def mock_rows():
    yield Row(["apt", "1", "2"])
    yield Row(["bat aa...ah", "1", "2"])
    yield Row(["can", "1", "2"])
    yield Row(["dot oo...eh", "1", "2"])
    yield Row(["wed", "1", "2"])
    yield Row(["zed"])


@pytest.fixture
def rowstack():
    return RowStack(mock_rows())


class Test_Rows:

    def test_pop(self, rowstack):
        assert rowstack.pop("bat", "dot") == [Row(['bat aa...ah', '1', '2']),
                                              Row(['can', '1', '2'])]

    def test_pop_segment_and_remaining_rows_behaviour(self, rowstack):
        a = rowstack.pop("bat", "dot")
        assert len(a) == 2
        b = rowstack.pop("apt", "wed")
        assert len(b) == 2
        c = rowstack.remaining_rows()
        assert c[0] == Row(['wed', '1', '2'])
        assert c[1] == Row(['zed'])


if __name__ == "__main__":
    pytest.main([__file__])
