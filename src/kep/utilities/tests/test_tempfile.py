import pathlib
from kep.utilities import TempFile


def test_TempFile():
    text = 'конь-огонь'
    with TempFile(text) as filename:
        assert text == pathlib.Path(filename).read_text(encoding='utf-8')
