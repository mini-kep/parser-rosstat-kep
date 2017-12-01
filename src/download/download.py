# -*- coding: utf-8 -*-
"""Download and unpack Word files from Rosstat web site."""

import os
import subprocess
import requests
import datetime

import config 

def download(url, path):
    r = requests.get(url.strip(), stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

def make_url(year, month):
    check_date(year, month)    
    month = str(month).zfill(2)
    return ('http://www.gks.ru/free_doc/doc_{}'.format(year) + \
            '/Ind/ind{}.rar'.format(month))

def check_date(year, month):
    def as_date(year, month):
        return datetime.date(year, month, 1)
    if as_date(year, month) < as_date(2016, 12):
        raise ValueError('No web files before 2016-12')

def unrar(path, folder, unrar=config.UNPACK_RAR_EXE):
    def mask_with_end_separator(folder):
        """UnRAR wants its folder argument  with '/'
        """
        return "{}{}".format(folder, os.sep)    
    folder = mask_with_end_separator(folder)
    assert folder.endswith("/") or folder.endswith("\\")
    tokens = [unrar, 'e', path, folder, '-y']
    exit_code = subprocess.check_call(tokens)
    return exit_code


class RemoteFile():

    def __init__(self, year, month):
        self.url = make_url(year, month)
        locfile = config.LocalRarFile(year, month)           
        self.path = locfile.path
        self.folder = locfile.folder

    @staticmethod
    def check_date(year, month):
        def as_date(year, month):
            return datetime.date(year, month, 1)
        if as_date(year, month) < as_date(2016, 12):
            raise ValueError('No web files before 2016-12')
            
    def download(self):
        download(self.url, self.path)
        print('Downloaded', self.path)

    def unrar(self):
        res = unrar(self.path, self.folder)
        if res == 0:
            print('UnRARed', self.path)       
            

    # FIXME: refactor to more compact code. 
    def clean(self):
        for file in os.listdir(self.folder):
            path = os.path.join(self.folder, file)
            if not path.endswith(".rar"):
                os.remove(path)
    # ------------------------------------


if __name__ == "__main__":
    u = RemoteFile(2016, 12)._make_url()
    assert u.startswith("http://www.gks.ru/free_doc/")

    rf = RemoteFile(2017, 6)
    rf.download()
    rf.unrar()
