"""Run full cycle of data processing from download to saving dataframe."""

from kep.vintage import Vintage, Latest
from kep.download.download import RemoteFile
from kep.word2csv.word import word2csv

# TODO: make xls file

def kep_run(year, month): # pragma: no cover
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


if '__main__' == __name__: # pragma: no cover
    # not todo: convert to docopt
    import sys
    command = sys.argv[1]
    year, month = (int(sys.argv[i]) for i in (2, 3))

    if command == 'download':
        # FIXME: when no data available, must not download file (currently in
        # is a 3kilobyte html error message, which is saved as rar file, causes error
        # elsewhere in a program
        remote = RemoteFile(year, month)
        remote.download()
        remote.unrar()

    if command == 'convert':
        word2csv(year, month)

    if command == 'parse':
        vint = Vintage(year, month)
        vint.validate()
        vint.save()

    if command == 'latest':        
        Latest(year, month).save()

    if command == 'xls':        
        Latest(year, month).to_excel()

    if command == 'upload':
        Latest(year, month).upload()

    if command == 'all':
        kep_run(year, month)
