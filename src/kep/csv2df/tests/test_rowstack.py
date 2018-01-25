import pytest

from kep.csv2df.reader import Row
from kep.csv2df.rowstack import RowStack

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

    def test_init(self):
        # FIXME: this is a very untransparent test!
                
        # ID: Test verifies that [r for r in rows] is equivalent to list(rows)
        # regardless if rows is generator or an iterable (e.g. a list)
        # This allows to make robust experiments to RowStack.__init__() method.
        def gen():
            yield Row(["dot oo...eh", "1", "2"])
            yield Row(["wed more text", "1", "2"])
            yield Row(["zed some text"])

        a_generator = gen()
        a_list = [
            Row(["dot oo...eh", "1", "2"]),
            Row(["wed more text", "1", "2"]),
            Row(["zed some text"]),
        ]

        from_generator = RowStack(a_generator)
        from_list = RowStack(a_list)

        assert from_generator.rows == from_list.rows

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