"""Download and unpack Word files from Rosstat web site."""

from pathlib import Path
import os
import subprocess
import requests
from datetime import date

UNRAR_EXE = str(Path(__file__).parent / 'bin' / 'UnRAR.exe')

def download(url, path):
    r = requests.get(url.strip(), stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            # filter out keep-alive new chunks
            if chunk:
                f.write(chunk)


def make_url(year, month):
    month = str(month).zfill(2)
    return (f'http://www.gks.ru/free_doc/doc_{year}/Ind/ind{month}.rar')

class Unpacker:
    def __init__(self, rar_path, destination_folder, unrar_executable=UNRAR_EXE):
        folder = self.mask_with_end_separator(destination_folder,)
        assert folder.endswith("/") or folder.endswith("\\")
        self.tokens = [unrar_executable, 'e', rar_path, folder, '-y']
        
    @staticmethod    
    def mask_with_end_separator(folder):
        """UnRAR wants its folder argument with '/'
        """
        return "{}{}".format(folder, os.sep)        

    def run(self):
         return subprocess.check_call(self.tokens)        


class Downloader():
    def __init__(self, year: int, month: int, 
                 destination_folder: str, 
                 unrar_executable = UNRAR_EXE):
        if date(year, month, 1) < date(2016, 12, 1):
            raise ValueError('No web files before 2016-12')
        self.url = make_url(year, month)
        self.folder = destination_folder

    @property
    def path(self):
        return os.path.join(self.folder, 'download.rar')

    def download(self):
        download(self.url, self.path)
        print('Downloaded', self.path)
        return True 

    def unpack(self):
        res = Unpacker(self.path, self.folder).run()
        if res == 0:
            print('UnRARed', self.path)
            return True
        else:
            return False


if __name__ == "__main__": #pragma: no cover
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        u = Downloader(2016, 12, tmpdirname)
        assert u.url.startswith("http://www.gks.ru/free_doc/")
        assert u.download()
        assert u.unpack()
        # TODO: clear temp folder

