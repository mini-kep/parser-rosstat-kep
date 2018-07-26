import yaml
import pathlib
import os


def read(incoming: str):
    txt = _file_or_string(incoming)
    return _str_to_yaml(txt)


def read_many(incoming: str):
    txt = _file_or_string(incoming)
    return _str_to_yaml_many(txt)


def read_text(filepath: str):
    return pathlib.Path(filepath).read_text(encoding='utf-8')


def _str_to_yaml(doc: str):
    return yaml.load(doc)


def _str_to_yaml_many(doc: str):
    return list(yaml.load_all(doc))


def _file_or_string(incoming: str):
    if os.path.exists(incoming):
        return read_text(incoming)
    else:
        return incoming