import pathlib
import yaml
# NOTE: see schema docs at https://github.com/keleshev/schema
from schema import Schema, Optional, Or, SchemaError

from kep.label import make_label

PATH_YAML_NAMER = pathlib.Path(__file__).with_name('namers.txt')


class Namer(object):
    _ALWAYS_VALID_START_LINE = ''

    def __init__(self, name, headers, units,
                 starts=None, ends=None, reader=None):
        self.name = name
        self.headers = self.iterate(headers)
        self.units = self.iterate(units)
        self.starts = self.iterate(starts) if starts else \
                      [self._ALWAYS_VALID_START_LINE]
        self.ends = self.iterate(ends)
        self.reader = reader

    @staticmethod
    def iterate(x):
        if isinstance(x, str):
            return [x]
        else:
            return x

    @property
    def labels(self):
        return set(make_label(self.name, unit) for unit in self.units)

    def inspect(self, tables):
        pass
        # WONTFIX:
        # is found header found not more than only once?

    def assert_all_labels_found(self, tables):
        diff = self.labels - {t.label for t in tables if t.is_defined()}
        if diff:
            raise ValueError(('Not found:', diff))

    def __repr__(self):
        return str(self.__dict__)

doc = pathlib.Path(PATH_YAML_NAMER).read_text(encoding='utf-8')
PARSING_DEFINTIONS = list(yaml.load(doc))

schema = Schema({'name': str,  # WONTFIX: all caps
                 'headers': Or(str, [str]),
                 'units': Or(str, [str]),
                 Optional('reader'): str,
                 Optional('starts'): Or(str, [str]),
                 Optional('ends'): Or(str, [str])
                 })

for p in PARSING_DEFINTIONS:
    try:
        schema.validate(p)
    except SchemaError:
        raise ValueError(p)

NAMERS = [Namer(x['name'], 
                x['headers'], 
                x['units'],
                x.get('starts'), 
                x.get('ends'), 
                x.get('reader'))
          for x in PARSING_DEFINTIONS]
