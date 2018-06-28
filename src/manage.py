"""Run full cycle of data processing from download to saving dataframe."""

from pathlib import Path
import shutil
from io import StringIO

import pandas as pd


from inputs import UNITS, YAML_DEFAULT, YAML_BY_SEGMENT
from parsing import create_parser
from util.remote import Downloader, Unpacker
from util.word import folder_to_csv
from util.dataframe import create_dataframe
from inputs.checkpoints import verify
from util.date import is_latest
from util.to_excel import save_excel


FREQUENCIES = list('aqm')
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / 'data'
OUTPUT_ROOT = PROJECT_ROOT / 'output'
assert DATA_ROOT.exists()
assert OUTPUT_ROOT.exists()


def md(folder):
    if not folder.exists():
        folder.mkdir(parents=True)
    return folder


class Locations(object):
    def __init__(self, year: int,
                 month: int,
                 data_root,
                 output_root):
        self.year = year
        self.month = month
        self.data = Path(data_root)
        self.out = Path(output_root)

    def inner_path(self, tag):
        if tag not in ('raw', 'interim', 'processed'):
            raise ValueError(tag)
        folder = self.data / tag / str(self.year) / str(self.month).zfill(2)
        return md(folder)

    @property
    def raw_folder(self):
        return self.inner_path('raw')

    @property
    def archive_filepath(self):
        return str(self.raw_folder / 'download.rar')

    @property
    def interim_csv(self):
        return self.inner_path('interim') / 'tab.csv'

    def processed_csv(self, freq: str):
        return self.inner_path('processed') / self.filename(freq)

    def latest_csv(self, freq: str):
        return md(self.data / 'processed' / 'latest') / self.filename(freq)

    @staticmethod
    def filename(freq):
        return 'df{}.csv'.format(freq)

    @property
    def xlsx(self):
        return str(self.out / 'kep.xlsx')

# not used


def make_reader(units=UNITS,
                default_yaml=YAML_DEFAULT,
                yaml_by_segment=YAML_BY_SEGMENT):
    return create_parser(units, default_yaml, yaml_by_segment)


def to_latest(year: int, month: int, loc):
    """Copy csv files from folder like *processed/2017/04* to
       *processed/latest*.
    """
    for freq in FREQUENCIES:
        src = loc.processed_csv(freq)
        dst = loc.latest_csv(freq)
        shutil.copyfile(str(src), str(dst))
        print("Updated", dst)
    print(f"Latest folder now refers to {loc.year}-{loc.month}")


def read_csv(source):
    """Wrapper for pd.read_csv1(). Treats first column at time index.

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
    loc = Locations(year, month, DATA_ROOT, OUTPUT_ROOT)
    filelike = proxy(loc.processed_csv(freq))
    return read_csv(filelike)


def update(year,
           month,
           units=UNITS,
           yaml_default=YAML_DEFAULT,
           yaml_by_segment=YAML_BY_SEGMENT,
           data_root=DATA_ROOT,
           output_root=OUTPUT_ROOT,
           validator=verify,
           force_download=False,
           force_unrar=False,
           force_convert_word=False):
    # filesystem
    loc = Locations(year, month, data_root, output_root)

    # perisist data
    d = Downloader(year, month, loc.archive_filepath)
    if force_download or not d.path.exists():
        d.run()
    print(d.status)
    u = Unpacker(loc.archive_filepath, loc.raw_folder)
    if force_unrar or not u.docs.exist():
        u.run()
    print(u.status)

    # convert Word to csv
    if force_convert_word or not loc.interim_csv.exists():
        folder_to_csv(loc.raw_folder, loc.interim_csv)

    # parse
    text = loc.interim_csv.read_text(encoding='utf-8')
    parse = create_parser(units, yaml_default, yaml_by_segment)
    values = list(parse(text))
    # save dataframes
    dfs = {}
    for freq in 'aqm':
        df = create_dataframe(values, freq)
        dfs[freq] = df
        validator(df, freq)
        df.to_csv(str(loc.processed_csv(freq)))
    if is_latest(year, month):
        to_latest(year, month, loc)
        save_excel(loc.xlsx, dfs)
    return dfs


if __name__ == '__main__':
    import sys
    try:
        year = int(sys.argv[1]) 
        month = int(sys.argv[2]) 
    except IndexError:
        year, month = 2018, 4                    
    dfs = update(year, month)
    dfa, dfq, dfm = (dfs[freq] for freq in FREQUENCIES)
