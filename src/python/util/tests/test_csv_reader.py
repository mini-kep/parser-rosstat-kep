from copy import copy

import pytest

from util.csv_reader import is_valid_row, yield_csv_rows, pop_rows

DOC = """__________
\t\t\t
Объем ВВП
1999\t4823
2000\t7306"""

ROWS = [['__________'],
        ['', '', '', ''],
        ['Объем ВВП'],
        ['1999', '4823'],
        ['2000', '7306']]

CLEAN_ROWS = [['Объем ВВП'],
              ['1999', '4823'],
              ['2000', '7306']]


class Test_is_valid_row:
    def test_returns_false(self):
        bad_rows = [
            [],
            ['', 'abc'],
            [None, 1],
            ["___"]
        ]
        for row in bad_rows:
            assert is_valid_row(row) is False

    def test_returns_true(self):
        assert is_valid_row(['abc'])


def test_yield_csv_rows():
    assert list(yield_csv_rows(DOC)) == ROWS


# Test Popper class
def mock_rows():
    yield ["apt extra text", "1", "2"]
    yield ["bat aa...ah", "1", "2"]
    yield ["can extra text", "1", "2"]
    yield ["dot oo...eh", "1", "2"]
    yield ["wed more text", "1", "2"]
    yield ["zed some text"]


def test_pop_rows():
    rows = list(mock_rows())
    a = pop_rows(rows, "bat", "dot")
    assert a == [["bat aa...ah", "1", "2"],
                 ["can extra text", "1", "2"]]


def test_pop_rows_remaining_rows_behaviour():
    rows = list(mock_rows())
    pop_rows(rows, "apt", "wed")
    assert rows[0] == ["wed more text", "1", "2"]
    assert rows[1] == ["zed some text"]


List0 = [['a', '5', 'z'],
         ['b', '4', 'x'],
         ['c', '1', 'z'],
         ['d', '2', 'y'],
         ['e', '3', 't']]


List1 = copy(List0)


def test_pop_rows_with_another_list_and_injection():
    assert pop_rows(List0, 'a', 'd') == List1[:3]
    assert List0 == List1[3:]


if __name__ == "__main__":
    pytest.main([__file__])
