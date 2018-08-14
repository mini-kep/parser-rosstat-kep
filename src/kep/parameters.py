"""Parsing parameters and checkpoints."""
from collections import OrderedDict
import pathlib
import yaml

from kep.engine.row import Datapoint

__all__ = ['ParsingParameters', 'CheckParameters']


def persist(filename):
    """Locate *filename* relative to current file."""
    return str(pathlib.Path(__file__).parent / 'yaml' / filename)


# -----------------------------------------------------------------------------

def _read_source(filename: str):
    return pathlib.Path(filename).read_text(encoding='utf-8')


def load_yaml_list(filename: str):
    """Load YAML contents of *filename*.

    Returns:
        list - each list element is a YAML document.
    """
    doc = _read_source(filename)
    return list(yaml.load_all(doc))


def load_yaml_one_document(filename: str):
    """Read from YAML file with one document."""
    docs = load_yaml_list(filename)
    assert len(docs) == 1
    return docs[0]


# -----------------------------------------------------------------------------


def read_by_key(filepath, pivot_key):
    """Read dictionaries from YAML file if *pivot_key*in keys."""
    return [x for x in load_yaml_list(filepath) if pivot_key in x.keys()]


# -----------------------------------------------------------------------------

def get_groups(filepath):
    def _key(d):
        return tuple(d)[0]
    items = load_yaml_one_document(filepath)
    return OrderedDict([(_key(x), x[_key(x)]) for x in items])

# -----------------------------------------------------------------------------


def get_mapper(filepath: str)-> dict:
    """Read unit mapper dictionary for *filepath*."""
    units_dict = load_yaml_one_document(filepath)
    return {pat: key for key, values in units_dict.items() for pat in values}

# -----------------------------------------------------------------------------


def split(string):
    string = string.replace('  ', ' ')
    return string.split(' ')


def to_datapoint(name: str, args: list):
    try:
        freq, year, month, value = args
    except ValueError:
        freq, year, value = args
        month = 12
    return Datapoint(name, freq, int(year), int(month), float(value))


def get_mandatory(filepath):
    """Return list of Datapoint instances."""
    doc = load_yaml_one_document(filepath)
    alls = []
    for string in doc['all']:
        name, *args = split(string)
        x = to_datapoint(name, args)
        alls.append(x)
    return alls


def get_optional(filepath):
    """Return list of lists of Datapoint instances.
       Will require at least one value from each list."""
    doc = load_yaml_one_document(filepath)
    anys = []
    for name, strings in doc['any'].items():
        x = [to_datapoint(name, split(s)) for s in strings]
        anys.append(x)
    return anys

# -----------------------------------------------------------------------------


i = persist('instructions.yml')
u = persist('base_units.yml')


class ParsingParameters:
    common_dicts = read_by_key(i, 'name')
    segment_dicts = read_by_key(i, 'start_with')
    units_dict = get_mapper(u)


c = persist('checkpoints.yml')
g = persist('groups.yml')


class CheckParameters:
    group_dict = get_groups(g)
    mandatory_list = get_mandatory(c)
    optional_lists = get_optional(c)
