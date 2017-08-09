import pytest
from collections import OrderedDict as odict
import io

from kep.rows import yield_csv_rows, to_rows, filter_csv_rows
from kep.rows import get_year, is_year, Row, RowStack

# FIXME: can I test open_csv?
# FIXME: is it ok to xfail missing tests?


@pytest.mark.xfail
def test_open_csv():
    # EP: don't know how to test this
    assert 0


junk_string = "________\n\n\t\t\t"
content_string = "Объем ВВП\n1999\t4823\n2000\t7306"
full_string = "\n".join([junk_string, content_string])


def test_yield_csv_rows():
    csvfile = io.StringIO(content_string)
    rows = list(yield_csv_rows(csvfile))
    assert rows[0] == ['Объем ВВП']
    assert rows[1] == ['1999', '4823']
    assert rows[2] == ['2000', '7306']


def test_filter_csv_rows():
    bad_rows_iter = iter([
        [],
        [None, 1],
        ["___"],
        ["abc"]
    ])
    gen = filter_csv_rows(bad_rows_iter)
    assert next(gen) == ["abc"]


def test_to_rows():
    csvfile = io.StringIO(full_string)
    rows = list(to_rows(csvfile))
    assert rows[0] == Row(['Объем ВВП'])
    assert rows[1] == Row(['1999', '4823'])
    assert rows[2] == Row(['2000', '7306'])


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
        assert str(self.row1) == "<Объем ВВП>"
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

        # FIXME: delete this
        # matches also can check multiple words
        # EP: this is so-so case, not sure what it ilustrates.
        # assert row.matches("words in") is True
        # EP: this is not expected behaviour, why any of the functions would mathch
        #     something not in order, pls delete
        # as long as they are in order
        #assert row.matches("words head") is False


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
        unit_mapper = odict([('% change', "rog"), ('%', "pct")])
        assert Row(["1. abcd, % change"]).get_unit(unit_mapper) == "rog"
        assert Row(["1. abcd, % change"]).get_unit(unit_mapper) != "pct"


def mock_rows():
    yield Row(["apt extra text", "1", "2"])
    yield Row(["bat aa...ah", "1", "2"])
    yield Row(["can extra text", "1", "2"])
    yield Row(["dot oo...eh", "1", "2"])
    yield Row(["wed more text", "1", "2"])
    yield Row(["zed some text"])


@pytest.fixture
def rowstack():
    return RowStack(mock_rows())


class Test_Rowstack:

    def test_pop(self, rowstack):
        a = rowstack.pop("bat", "dot")
        assert a == [Row(["bat aa...ah", "1", "2"]),
                     Row(["can extra text", "1", "2"])]

    def test_pop_segment_and_remaining_rows_behaviour(self, rowstack):
        b = rowstack.pop("apt", "wed")
        assert len(b) == 4
        c = rowstack.remaining_rows()
        assert c[0] == Row(["wed more text", "1", "2"])
        assert c[1] == Row(["zed some text"])

    @pytest.mark.xfail
    def test_yield_segment_with_defintion(self):
        # will need a mock for specification or a specification instance/fixture (can copy from example1.py)
        # need - 1 segment, 1 default definition for *rowstack* fixture
        assert 0


if __name__ == "__main__":
    pytest.main([__file__])
