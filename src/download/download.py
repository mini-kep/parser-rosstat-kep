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

# TODO: make test
#        assert folder.endswith("/") or folder.endswith("\\")

class Unpacker:
    def __init__(self, archive_filepath, destination_folder, unrar_executable=UNRAR_EXE):
        self.folder = self.mask_with_end_separator(destination_folder)
        self.tokens = [unrar_executable, 'e', archive_filepath, self.folder, '-y']
        
    @staticmethod    
    def mask_with_end_separator(folder):
        """UnRAR wants its folder argument with '/'
        """
        return "{}{}".format(folder, os.sep)        

    def run(self):
        try:
            return subprocess.check_call(self.tokens) 
        except subprocess.CalledProcessError as e:
            print('Cannot execute:', ' '.join(self.tokens))
            raise e

    def find_files(self, glob_pattern):
        return list(Path(self.folder).glob(glob_pattern))

    def unpack(self, force=False):
        doc_files = self.find_files('*.doc*')
        if doc_files and not force:
            print('Already unpacked:\n    ', '\n     '.join(map(str, doc_files)))
            return True
        res = self.run()
        if res == 0:
            print('UnRARed', self.folder)
            return True
        return False


class Downloader():
    def __init__(self, year: int, month: int, 
                 destination_local_file: str, 
                 unrar_executable = UNRAR_EXE):
        if date(year, month, 1) < date(2016, 12, 1):
            raise ValueError('No web files before 2016-12')
        self.url = make_url(year, month)
        self.path = destination_local_file


    def download(self, force=False):
        if os.path.exists(self.path) and not force:
            print('Already downloaded:\n    ', self.path)
            return True
        download(self.url, self.path)
        print('Downloaded', self.path)
        return True



if __name__ == "__main__": #pragma: no cover
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdirname:
        u = Downloader(2016, 12, tmpdirname)
        assert u.url.startswith("http://www.gks.ru/free_doc/")
        assert u.download()

