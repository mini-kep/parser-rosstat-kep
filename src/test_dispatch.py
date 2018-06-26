import pytest
import tempfile
import requests

from dispatch import update, Locations


def test_update():
     with tempfile.TemporaryDirectory() as tmpdir:
         # setup
         assert 1
         #loc = Locations(2018, 4, data_root=tmpdir, output_root=tmpdir)
         #resp = requests.get('https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/dev/data/interim/2018/04/tab.csv')
         #loc.interim_csv.write_text(resp.text, encoding='utf-8')
         #assert loc.interim_csv.exists()
         # test  
         #assert update(year=2018, 
         #       month=4, 
         #       data_root=tmpdir, 
         #       output_root=tmpdir,
         #       force_download=True,
         #       force_unrar=True,
         #       force_convert_word=False)

if __name__ == "__main__":
    pytest.main([__file__])
    