import os

import config
from download.download import RemoteFile
from word2csv.word import folder_to_csv 
from csv2df.runner import Vintage


def run(year, month):
    #download and unpack
    remote = RemoteFile(year, month)
    remote.download()
    remote.unrar()
    
    # make interim csv from Word files
    raw_folder = config.DataFolder(year, month).raw
    interim_csv = config.LocalCSV(year, month).interim
    if not os.path.exists(interim_csv):
        folder_to_csv(folder=raw_folder, 
                      csv_filename=interim_csv)
    
    #parse, validate, save
    vint = Vintage(year, month)
    vint.validate()
    vint.save()