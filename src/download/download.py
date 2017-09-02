# -*- coding: utf-8 -*-
"""Download and unpack Word files from Rosstat web site
   to 'data/raw/<year>/<month>' folder.
"""

import os
import subprocess
import requests
import datetime

from config import PathHelper

UNPACK_RAR_EXE = PathHelper.get_unrar_binary()


def download(url, path):
    r = requests.get(url.strip(), stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def _mask_with_end_separator(folder):
    """UnRAR wants its folder parameter to send with /
       This function supllies a valid folder argument for UnRAR."""
    return "{}{}".format(folder, os.sep)


def unrar(path, folder, unrar=UNPACK_RAR_EXE):
    folder = _mask_with_end_separator(folder)
    assert folder.endswith("/") or folder.endswith("\\")
    tokens = [unrar, 'e', path, folder, '-y']
    exit_code = subprocess.check_call(tokens)
    return exit_code


class RemoteFile():

    def __init__(self, year, month, helper = PathHelper):
        self.year, self.month = year, month
        self._check_date()
        self.url = self._make_url()
        folder = helper.get_raw_folder(year, month)
        self.folder = str(folder)
        self.local_path = str(folder / 'ind.rar')

    def _check_date(self):
        def as_date(year, month):
            return datetime.date(year, month, 1)
        if as_date(self.year, self.month) < as_date(2016, 12):
            raise ValueError('No web files before 2016-12')

    def _make_url(self):
        month = str(self.month).zfill(2)
        year = self.year
        return f'http://www.gks.ru/free_doc/doc_{year}/Ind/ind{month}.rar'

    def download(self, force=False):
        must_run = True
        if os.path.exists(self.local_path):
            must_run = False
        if force:
            must_run = True
        if must_run:
            download(self.url, self.local_path)
        if os.path.exists(self.local_path):
            print('Downloaded', self.local_path)
            return True
        else:
            print('Already downloaded', self.local_path)
            return False

    def unrar(self):
        res = unrar(self.local_path, self.folder)
        if res == 0:
            print('UnRARed', self.local_path)
            return True
        else:
            return False

    def clean(self):
        for file in os.listdir(self.folder):
            path = os.path.join(self.folder, file)
            if not path.endswith(".rar"):
                os.remove(path)


if __name__ == "__main__":
    u = RemoteFile(2016, 12)._make_url()
    assert u.startswith("http://www.gks.ru/free_doc/")

    rf = RemoteFile(2017, 6)
    rf.download()
    rf.unrar()

# May use messages:

#    def _rar_content(self):
#        """Return single filename stored in RAR archive."""
#        return subprocess.check_output([
#            UNPACK_RAR_EXE,
#            'lb', self.rar_path]).decode("utf-8").strip()
#
#    # public methods download, unrar, get_filename
#    def download(self):
#        if os.path.exists(self.rar_path):
#            print("Already downloaded:", self.rar_path)
#        else:
#            print("Downloading:", self.url)
#            self._download(self.url, self.rar_path)
#            print("Saved as:", self.rar_path)
#            self._init_csv_filename()
#        return self
#
#    def unrar(self):
#        if os.path.exists(self.csv_path):
#            print("Already unpacked:", self.csv_path)
#        else:
#            print("Unpacking:", self.csv_path)
#            self._unrar(self.rar_path, folder=Folder('raw_csv').path())
#        return self.csv_path
