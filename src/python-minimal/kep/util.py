import yaml
import pathlib
import os


def read(incoming: str):
    txt = file_or_string(incoming)
    return str_to_yaml(txt)


def read_many(incoming: str):
    txt = file_or_string(incoming)
    return str_to_yaml_many(txt)


def read_text(filepath: str):
    return pathlib.Path(filepath).read_text(encoding='utf-8')


def read_yaml(filepath: str):
    doc = read_text(filepath)
    return str_to_yaml(doc)


def str_to_yaml(doc: str):
    return yaml.load(doc)


def str_to_yaml_many(doc: str):
    return list(yaml.load_all(doc))


assert str_to_yaml_many("""- abc\n- def""") == [['abc', 'def']]


def file_or_string(incoming: str):
    if os.path.exists(incoming):
        return read_text(incoming)
    else:
        return incoming


def iterate(x):
    if isinstance(x, str):
        return [x]
    else:
        return x
