# -*- coding: utf-8 -*-
"""Download and unpack Word files from Rosstat web site."""

import os
import subprocess
import requests
import datetime

import config 

UNPACK_RAR_EXE = config.UNPACK_RAR_EXE

def download(url, path):
    r = requests.get(url.strip(), stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def mask_with_end_separator(folder):
    """UnRAR wants its folder parameter to send with /
       This function supplies a valid folder argument for UnRAR."""
    return "{}{}".format(folder, os.sep)


def unrar(path, folder, unrar=UNPACK_RAR_EXE):
    folder = mask_with_end_separator(folder)
    assert folder.endswith("/") or folder.endswith("\\")
    tokens = [unrar, 'e', path, folder, '-y']
    exit_code = subprocess.check_call(tokens)
    return exit_code


class LocalFile:
    def __init__(self, year, month):        
        self._folder = config.DataFolder(year, month).raw
    
    @property
    def folder(self):
        return str(self._folder)
    
    @property
    def path(self):
        return str(self._folder / 'ind.rar')

class RemoteFile():

    def __init__(self, year, month):
        self.check_date(year, month)
        self.year, self.month = year, month    
        lf = LocalFile(year, month)           
        self.path = lf.path
        self.folder = lf.folder

    @staticmethod
    def check_date(year, month):
        def as_date(year, month):
            return datetime.date(year, month, 1)
        if as_date(year, month) < as_date(2016, 12):
            raise ValueError('No web files before 2016-12')
            
    @property
    def url(self):
        month = str(self.month).zfill(2)
        year = self.year
        return f'http://www.gks.ru/free_doc/doc_{year}/Ind/ind{month}.rar'

    def download(self):
        download(self.url, self.path)
        print('Downloaded', self.path)

    def unrar(self):
        res = unrar(self.path, self.folder)
        if res == 0:
            print('UnRARed', self.path)
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
