# -*- coding: utf-8 -*-
"""Download and unpack Word files from Rosstat web site."""

import os
import subprocess
import requests
from datetime import date

import config 

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


def unrar(path, folder, unrar=config.UNPACK_RAR_EXE):
    def mask_with_end_separator(folder):
        """UnRAR wants its folder argument with '/'
        """
        return "{}{}".format(folder, os.sep)    
    folder = mask_with_end_separator(folder)
    # FIXME: replace assert
    assert folder.endswith("/") or folder.endswith("\\")
    tokens = [unrar, 'e', path, folder, '-y']
    exit_code = subprocess.check_call(tokens)
    return exit_code


class RemoteFile():

    def __init__(self, year, month):
        self.year, self.month = year, month
        self.url = make_url(year, month)
        locfile = config.LocalRarFile(year, month)           
        self.path = locfile.path
        self.folder = locfile.folder

    def check_date(self):
        if date(self.year, self.month, 1) < date(2016, 12, 1):
            raise ValueError('No web files before 2016-12')
            
    def download(self):
        self.check_date()
        download(self.url, self.path)
        print('Downloaded', self.path)

    def unrar(self):
        res = unrar(self.path, self.folder)
        if res == 0:
            print('UnRARed', self.path) 


if __name__ == "__main__":
    u = RemoteFile(2016, 12).url
    assert u.startswith("http://www.gks.ru/free_doc/")
    u.download()
    u.unrar()
