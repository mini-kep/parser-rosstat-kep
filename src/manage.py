import os

import config
from download.download import RemoteFile
from word2csv.word import word2csv 
from csv2df.runner import Vintage
import shutil


def run(year, month):
    #download and unpack
    remote = RemoteFile(year, month)
    remote.download()
    remote.unrar()
    
    # make interim csv from Word files
    word2csv(year, month)
    
    #parse interim csv, validate, save
    vint = Vintage(year, month)
    vint.validate()
    vint.save()
    
def copy_latest():
    """Copy csv files from folder like 
           *processed/2017/04* 
        to 
           *processed/latest* folder.
    """
    year, month = config.LATEST_DATE
    csv_file = config.LocalCSV(year, month)
    latest = config.Latest
    for freq in config.FREQUENCIES:
        src = csv_file.processed(freq)
        dst = latest.csv(freq) 
        shutil.copyfile(src, dst)
        print('Copied', src)    
    