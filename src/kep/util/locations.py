from pathlib import Path

from kep.util.dates import assert_supported
from kep.config import DATA_ROOT, OUTPUT_ROOT


def as_string(func):
    def wrapper(*arg, **kwarg):
        return str(func(*arg, **kwarg))
    return wrapper

def md(folder):
    if not folder.exists():
        folder.mkdir(parents=True)
    return folder


def _inner_folder(data_root, tag, year, month):
    return md(data_root / tag / str(year) / str(month).zfill(2))


def inner_folder(data_root, tag, year, month):
    """Protective version of _inner_folder()"""
    assert_supported(year, month)
    allowed_tags = ('raw', 'interim', 'processed')
    if tag in allowed_tags:
        return _inner_folder(data_root, tag, year, month)
    else:
        raise ValueError(f'{tag} not supported, use be any of {allowed_tags}')


def latest_folder(data_root=DATA_ROOT):
    return data_root / 'processed' / 'latest'


@as_string
def xl_location():
    return OUTPUT_ROOT / 'kep.xlsx'


@as_string
def raw_folder(year, month, data_root=DATA_ROOT):
    return inner_folder(data_root, 'raw', year, month)


@as_string
def rarfile(year, month):
    return Path(raw_folder(year, month)) / 'download.rar'


@as_string
def parsing_instructions(data_root=DATA_ROOT):
    return data_root / 'instructions.txt'


@as_string
def unit_mapper(data_root=DATA_ROOT):
    return data_root / 'base_units.txt'

@as_string
def checkpoints(data_root=DATA_ROOT):
    return data_root / 'checkpoints.txt'


@as_string
def interim_csv(year: int, month: int, data_root=DATA_ROOT):
    return inner_folder(data_root, 'interim', year, month) / 'tab.csv'


def filename(freq):
    return 'df{}.csv'.format(freq)


@as_string
def processed_csv(year, month, freq: str, data_root=DATA_ROOT):
    return inner_folder(data_root, 'processed', year, month) / filename(freq)


@as_string
def latest_csv(freq: str, data_root=DATA_ROOT):
    return latest_folder(data_root) / filename(freq)
