import pathlib
import yaml
import os

from kep.definition.namers import NAMERS
from kep.definition.namers import UNITS
from kep.reader import to_values
import kep.reader as reader

datafolder = pathlib.Path(__file__).parent / 'data'
PATH = str(datafolder / 'tab.csv')
PATH_LEGACY = str(datafolder / 'tab_old.csv')
PATH_CHECKPOINTS = os.path.join('data', 'checkpoints.yaml')


def messup(values):
    """Produce wrong values for year and cells."""
    messed_years = set()
    messed_values = set()
    for v in reader.to_values(PATH, UNITS, NAMERS):
        year = v['year']
        value = v['value'].replace(',', '.').replace('…', '')
        try:
            assert int(year) <= 2018 and int(year) >= 1998
        except BaseException:
            messed_years.add(year)
        try:
            float(value) if value else 0
        except BaseException:
            messed_values.add(value)
    return messed_years, messed_values


def save_checkpoints():
    """Persisting checkpoints. Write first and last values
       of each time series to file 'checkpoints.yaml'.
    """
    expected_values = []
    for namer in NAMERS:
        param = PATH, UNITS, [namer]
        tables = reader.parsed_tables(*param)
        namer.assert_all_labels_found(tables)
        data = reader.to_values(*param)
        print(namer.name)
        for label in namer.labels:
            subdata = [x for x in data if x['label'] == label]
            a, z = subdata[0], subdata[-1]
            expected_values.extend([a, z])
            print(label)
            print(a)
            print(z)
    pathlib.Path(PATH_CHECKPOINTS ).write_text(yaml.dump(expected_values))


if __name__ == "__main__":
    messed_years, messed_values = messup(to_values(PATH))
