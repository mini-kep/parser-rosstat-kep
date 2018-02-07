import pytest
from ..download import RemoteFile

def test_RemoteFile():
    u = RemoteFile(2016, 12)
    assert u.url.startswith("http://www.gks.ru/free_doc/") 

def test_RemoteFile_check_date_negative():
    u = RemoteFile(2016, 11)
    with pytest.raises(ValueError):
        u.check_date()        