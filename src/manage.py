"""Run full cycle of data processing from download to saving dataframe."""

from kep.vintage import Vintage
from kep.download.download import RemoteFile
from kep.word2csv.word import word2csv
from kep.helper.path import copy_to_latest_folder


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


if '__main__' == __name__: # pragma: no cover
    import sys
    command = sys.argv[1]
    year, month = (int(sys.argv[i]) for i in (2, 3))

    if command == 'download':
        # FIXME: when no data available, must not download file (currently in
        # is a #k html error message)
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
        # FIXME: need a safeguard in last 2 SUPPORTED_DATES
        copy_to_latest_folder(year, month)

    if command == 'upload':
        # TODO: upload latest data to database
        raise NotImplementedError

    if command == 'all':
        run(year, month)
