import io
import pytest

from kep.csv2df.row_model import Row
from kep.csv2df.row_stack import (RowStack, is_valid_row, yield_csv_rows,
                                  text_to_rows)   


junk_string = "________\n\n\t\t\t"
content_string = "Объем ВВП\n1999\t4823\n2000\t7306"
full_string = "\n".join([junk_string, content_string])


def test_yield_csv_rows():
    filelike = io.StringIO(content_string)
    rows = list(yield_csv_rows(filelike))
    assert rows[0] == ["Объем ВВП"]
    assert rows[1] == ["1999", "4823"]
    assert rows[2] == ["2000", "7306"]


def test_is_valid_row():
    bad_rows = [
        [],
        ['', 'abc'],
        [None, 1],
        ["___"]
    ]
    for row in bad_rows:
        assert is_valid_row(row) is False
    assert is_valid_row(['abc'])


def test_text_to_rows():
    rows = list(text_to_rows(content_string))
    assert rows[0] == Row(["Объем ВВП"])
    assert rows[1] == Row(["1999", "4823"])
    assert rows[2] == Row(["2000", "7306"])
    

def mock_rows():
    yield ["apt extra text", "1", "2"]
    yield ["bat aa...ah", "1", "2"]
    yield ["can extra text", "1", "2"]
    yield ["dot oo...eh", "1", "2"]
    yield ["wed more text", "1", "2"]
    yield ["zed some text"]

csv_rows = '\n'.join(['\t'.join(row) for row in mock_rows()])

@pytest.fixture
def rowstack():   
    return RowStack(csv_rows)


class Test_Rowstack:

    def test_init(self, rowstack):
        assert isinstance(rowstack.rows, list)
        assert len(rowstack.rows) == 6

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

if __name__ == "__main__":
    pytest.main([__file__])
    