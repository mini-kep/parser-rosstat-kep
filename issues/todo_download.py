# -*- coding: utf-8 -*-
"""Download and unpack Word files from Rosstat web site."""

import requests
import subprocess
from path import Path

accepted_web_dates = [(2016, 12), 
                      (2017, 1), (2017, 2), (2017, 3), (2017, 4), (2017, 5)]


def make_url(year, month):
    if (year, month) not in accepted_web_dates: 
        raise ValueError
    month = str(month).zfill(2)    
    return "http://www.gks.ru/free_doc/doc_{0}/Ind/ind{1}.rar".format(year, month)

assert make_url(2016, 12).startswith("http://www.gks.ru/free_doc/")
 

def make_local_path(year, month):
    # FIXME: must be in data/raw folder
    return "{}-{}.rar".format(year, month)

assert make_url(2016, 12).endswith(".rar")


def download(url, path):
    r = requests.get(url.strip(), stream=True)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


UNPACK_RAR_EXE = "UnRAR.exe"

   
def unrar(path, folder="./unpack/"):
    commands = [UNPACK_RAR_EXE, 'e', path, folder, '-y']
    # will not reconise it is a directory unless ends with a (back)slash 
    assert folder.endswith("/") or folder.endswith("\\") 
    exit_code = subprocess.check_call(commands)
    return exit_code 

if __name__ == "__main__":
    url = make_url(2016, 12)
    path = make_local_path(2016, 12)
    if not Path(path).exists:
        download(url, path)
        
    a = unrar(path)  
    #exited with success code 0
    assert a == 0     


#class RawDataset():
#
#    def __init__(self, year):
#        self.year = year
#        self.url = URL[year]
#        # RAR file path
#        rar_filename = self.url.split('/')[-1]
#        self.rar_path = Folder('rar').filepath(rar_filename)
#        # Rosstat raw CSV file path
#        self._init_csv_filename()
#
#    def _init_csv_filename(self):
#        if os.path.exists(self.rar_path):
#            csv_filename = self._rar_content()
#            self.csv_path = Folder('raw_csv').filepath(csv_filename) 
#        else:
#            self.csv_path = ''
#
#    @staticmethod
#    def _download(url, path):
#        r = requests.get(url.strip(), stream=True)
#        with open(path, 'wb') as f:
#            for chunk in r.iter_content(chunk_size=1024):
#                if chunk:  # filter out keep-alive new chunks
#                    f.write(chunk)
#        return path
#
#    @staticmethod
#    def _unrar(path, folder):
#        subprocess.check_call([
#            UNPACK_RAR_EXE,
#            'e', path,
#            folder,
#            '-y'
#        ])
#
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
#
#    # todo: change name to 'get_raw_csv_path' using IDE
#    def get_filename(self):
#        if os.path.exists(self.csv_path):
#            return self.csv_path
#        else:
#            msg = "Source CSV file for year {} not found. ".format(self.year) +\
#                  "\nUse RawDataset({}).download().unrar() to proceed.".format(self.year)
#            raise FileNotFoundError(msg)
#
#
#if __name__ == "__main__":
#    # RawDataset(2012).download().unrar()
#    # RawDataset(2013).download().unrar()
#    # RawDataset(2014).download().unrar()
#    # RawDataset(2015).download().unrar()
#print(RawDataset(2012).get_filename())