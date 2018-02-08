import pytest
from ..download import RemoteFile, make_url


def test_make_url_will_not_work_without_fstring_format():
    year = 2017
    month = 2
    url = make_url(year, month)
    assert '{' not in url

def test_RemoteFile():
    u = RemoteFile(2016, 12)
    assert u.url.startswith("http://www.gks.ru/free_doc/") 

def test_RemoteFile_check_date_negative():
    u = RemoteFile(2016, 11)
    with pytest.raises(ValueError):
        u.check_date()        