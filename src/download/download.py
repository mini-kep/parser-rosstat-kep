"""Download and unpack Word files from Rosstat web site."""

from pathlib import Path
import os
import platform
import subprocess
import requests
from datetime import date

IS_WINDOWS = (platform.system() == 'Windows')
if IS_WINDOWS:
    UNRAR_EXE = str(Path(__file__).parent / 'bin' / 'UnRAR.exe')
else:
    UNRAR_EXE = 'unrar'


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


class DocFiles:
    def __init__(self, folder):
        self.folder = Path(folder)

    @property
    def paths(self):
        return [str(x) for x in self.folder.glob('*.doc*')]

    def exist(self):
        return len(self.paths) > 0

    def __str__(self):
        return ' ' * 4 + ('\n' + ' ' * 4).join(self.paths)


class Unpacker:
    def __init__(self, archive_filepath,
                 destination_folder,
                 unrar_executable=UNRAR_EXE):
        if not Path(archive_filepath).exists():
            raise FileNotFoundError(archive_filepath)
        self.path = archive_filepath
        self.folder = destination_folder
        self.unrar_executable = unrar_executable
        self.status = (f'Already unpacked:\n{self.docs}'
                       if self.docs.exist()
                       else None)

    @property
    def docs(self):
        return DocFiles(self.folder)

    @property
    def tokens(self):
        # UnRAR wants its folder argument with '/'
        folder = "{}{}".format(self.folder, os.sep)
        return [str(self.unrar_executable), 'e', str(self.path), folder, '-y']

    def _call(self):
        try:
            return subprocess.check_call(self.tokens)
        except subprocess.CalledProcessError as e:
            self.status = 'Cannot execute:' + ' '.join(self.tokens)
            raise e

    def run(self):
        res = self._call()
        if res == 0:
            self.status = f'UnRARed {self.path}'
            return True
        return False


class Downloader():
    def __init__(self, year: int, month: int,
                 local_filepath: str,
                 unrar_executable=UNRAR_EXE):
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


# TODO: make test
#        assert folder.endswith("/") or folder.endswith("\\")

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
    with pytest.raises(FileNotFoundError):
        u = Unpacker(path, path)
