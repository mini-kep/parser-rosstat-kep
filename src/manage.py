import config
from download.download import RemoteFile
from word2csv.word import word2csv 
from vintage import Vintage
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
    csv_file = config.ProcessedCSV(year, month)
    latest = config.Latest
    for freq in config.FREQUENCIES:
        src = csv_file.path(freq)
        dst = latest.csv(freq) 
        shutil.copyfile(src, dst)
        print('Copied', src)   
        
if '__main__' == __name__:
    # same lines are run in 'invoke add 2017 10'
    year, month = 2017, 10 
    #remote = RemoteFile(year, month)
    #remote.download()      
    #remote.unrar()
    #word2csv(year, month)
    vint = Vintage(year, month)
    vint.validate()
    vint.save()
    copy_latest()
    
    # MAY DO:
    # - may use a webhook to upload to database
    # - can import parser code to upload to database from here
    # - check the data is in database
    
    
    
    
