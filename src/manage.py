"""Run full cycle of data processing from download to saving dataframe."""

from kep.extractor import Vintage
from kep.download.download import RemoteFile
from kep.word2csv.word import word2csv


def run(year, month):
    #download and unpack
    remote = RemoteFile(year, month)
    remote.download()
    remote.unrar()

    # make interim csv from Word files
    word2csv(year, month)

    # parse interim csv, validate, save
    vint = Vintage(year, month)
    vint.validate()
    vint.save()


if '__main__' == __name__:
    import sys
    command = sys.argv[1]
    year, month = (int(sys.argv[i]) for i in (2,3))
    
    if command == 'download':
        # FIXME: when no data, must not download file 
        remote = RemoteFile(year, month)
        remote.download()
        remote.unrar()

    if command == 'convert':
        word2csv(year, month)

    if command == 'parse':
        vint = Vintage(year, month)
        vint.validate()
        vint.save()

    if command == 'upload':
        # TODO: upload method to database
        raise NotImplementedError        

    if command == 'all':
        run(year, month)