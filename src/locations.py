"""Manage dataset by year and month:

   download(year, month)
   unpack(year, month)
   make_interim_csv(year, month)
   parse_and_save(year, month)
   to_latest(year, month)
   to_excel(year, month)

File access:
    get_dataframe(year, month, freq)

"""
from pathlib import Path
from io import StringIO
import pandas as pd
import shutil
import kep

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / 'data'
OUTPUT_ROOT = PROJECT_ROOT / 'output'
assert DATA_ROOT.exists()
assert OUTPUT_ROOT.exists()


def echo(func):
    def wrapper(*arg, **kwarg):
        msg = func(*arg, **kwarg)
        print(msg)
    return wrapper


def as_string(func):
    def wrapper(*arg, **kwarg):
        return str(func(*arg, **kwarg))
    return wrapper


@echo
def download(year, month, force=False):
    filepath = rarfile(year, month)
    return kep.download(year, month, filepath, force)


@echo
def unpack(year, month, force=False):
    filepath = rarfile(year, month)
    folder = raw_folder(year, month)
    return kep.unpack(filepath, folder, force)


@echo
def make_interim_csv(year, month, force=False):
    folder = raw_folder(year, month)
    filepath = interim_csv(year, month)
    return kep.folder_to_csv(folder, filepath)


@echo
def parse_and_save(year, month, force=False):
    dfs = parse_to_dataframes(year, month)
    return save(year, month, *dfs)


def parse_to_dataframes(year, month):
    s = kep.session.Session(unit_mapper(), parsing_instructions())
    csv_source = interim_csv(year, month)
    s.parse(csv_source)
    return s.dataframes()


def save(year, month, dfa, dfq, dfm):
    for df, freq in zip([dfa, dfq, dfm], 'aqm'):
        path = processed_csv(year, month, freq)
        df.to_csv(path)
        return "Saved dataframe to {}".format(path)


def md(folder):
    if not folder.exists():
        folder.mkdir(parents=True)
    return folder


def _inner_folder(data_root, tag, year, month):
    return md(data_root / tag / str(year) / str(month).zfill(2))


def inner_folder(data_root, tag, year, month):
    """Protective version of _inner_folder()"""
    kep.dates.assert_supported(year, month)
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


@echo
def to_excel(year: int, month: int):
    dfs = {f'df{freq}': get_dataframe(year, month, freq) for freq in 'aqm'}
    path = xl_location()
    return kep.save_excel(path, **dfs)


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


@echo
def to_latest(year: int, month: int):
    """Copy CSV files from folder like *processed/2017/04* to *processed/latest*.
    """
    for freq in 'aqm':
        src = processed_csv(year, month, freq)
        dst = latest_csv(freq)
        shutil.copyfile(src, dst)
        print("Updated", dst)
    return f"Latest folder now refers to {year}-{month}"


def read_csv(source):
    """Wrapper for pd.read_csv(). Treats first column as time index.
       Returns:
           pd.DataFrame()
    """
    converter_arg = dict(converters={0: pd.to_datetime}, index_col=0)
    return pd.read_csv(source, **converter_arg)


def proxy(path):
    """A workaround for pandas problem with non-ASCII paths on Windows
       See <https://github.com/pandas-dev/pandas/issues/15086>
       Args:
           path (pathlib.Path) - CSV filepath
       Returns:
           io.StringIO with CSV content
    """
    content = Path(path).read_text()
    return StringIO(content)


def get_dataframe(year, month, freq):
    """Read dataframe from local folder"""
    path = processed_csv(year, month, freq)
    filelike = proxy(path)
    return read_csv(filelike)
