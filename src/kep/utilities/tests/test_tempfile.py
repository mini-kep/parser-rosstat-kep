import pathlib
from kep.utilities import TempFile

def test_TempFile():
    text = 'конь-огонь'
    with TempFile(text) as filename:
        assert text == pathlib.Path(filename).read_text(encoding='utf-8')        


def test_TempFile_is_not_readable_on_different_encoding():
    text = 'конь-огонь'
    with TempFile(text) as filename:
        assert text != pathlib.Path(filename).read_text()  




