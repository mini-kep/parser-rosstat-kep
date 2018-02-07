from ..download import RemoteFile

def test_RemoteFile():
    u = RemoteFile(2016, 12)
    assert u.url.startswith("http://www.gks.ru/free_doc/") 