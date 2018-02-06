import pytest

from kep.csv2df.reader import is_valid_row, yield_csv_rows, text_to_list, Popper

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

def test_yield_csv_rows():
    assert list(yield_csv_rows(DOC)) == ROWS

def test_text_to_rows():
    assert text_to_list(DOC) == CLEAN_ROWS 

    
# Test Popper class    
def mock_rows():
    yield ["apt extra text", "1", "2"]
    yield ["bat aa...ah", "1", "2"]
    yield ["can extra text", "1", "2"]
    yield ["dot oo...eh", "1", "2"]
    yield ["wed more text", "1", "2"]
    yield ["zed some text"]

csv_rows = '\n'.join(['\t'.join(row) for row in mock_rows()])

@pytest.fixture
def popper():   
    return Popper(csv_rows)


class Test_Popper:

    def test_init(self, popper):
        assert isinstance(popper.rows, list)
        assert len(popper.rows) == 6
        assert isinstance(popper.rows[0], list) 
        assert popper.rows[0][0] == "apt extra text"


    def test_pop(self, popper):
        a = popper.pop("bat", "dot")
        assert a == [["bat aa...ah", "1", "2"],
                     ["can extra text", "1", "2"]]

    def test_pop_segment_and_remaining_rows_behaviour(self, popper):
        b = popper.pop("apt", "wed")
        assert len(b) == 4
        c = popper.remaining_rows()
        assert c[0] == ["wed more text", "1", "2"]
        assert c[1] == ["zed some text"]        

if __name__ == "__main__":
    pytest.main([__file__])
    