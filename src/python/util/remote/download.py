"""Download and unpack Word files from Rosstat web site."""

from datetime import date
import requests
from pathlib import Path


def download(url, path):
    r = requests.get(url.strip(), stream=True)
    with open(str(path), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            # filter out keep-alive new chunks
            if chunk:
                f.write(chunk)


def make_url(year, month):
    month = str(month).zfill(2)
    return (f'http://www.gks.ru/free_doc/doc_{year}/Ind/ind{month}.rar')


class Downloader():
    def __init__(self, year: int, month: int,
                 local_filepath: str):
        if date(year, month, 1) < date(2016, 12, 1):
            raise ValueError('No web files before 2016-12')
        self.url = make_url(year, month)
        self.path = Path(local_filepath)
        self.status = (f'Already downloaded:\n    {self.path}'
                       if self.path.exists()
                       else None)

    def run(self):
        download(self.url, self.path)
        self.status = f'Downloaded {self.path}'
        return True


if __name__ == "__main__":  # pragma: no cover
    import tempfile
    import pytest
    with tempfile.NamedTemporaryFile() as f:
        path = f.name
    d = Downloader(2016, 12, path)
    assert d.url.startswith("http://www.gks.ru/free_doc/")
    assert d.run()
    assert Path(path).lstat().st_size > 1000
    Path(path).unlink()
