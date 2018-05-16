"""Run full cycle of data processing from download to saving dataframe."""

from kep.download.download import RemoteFile
from kep.word2csv.word import word2csv
from kep.vintage import Vintage

def run(year, month): # pragma: no cover
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
