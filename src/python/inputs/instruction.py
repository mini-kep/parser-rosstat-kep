"""Parsing definition to identify tables in the data source file.

   A defnition contains a list of nested dicts.

   Each dict has following keys:
   - commands, a list of dicts each with following keys:
       - variable name ('GDP')
       - corresponding headers ('Oбъем ВВП')
       - units of measurement ('bln_rub')
   - boundaries (start and end lines of text)
   - reader function name(string)

"""

import yaml


def iterate(x):
    if isinstance(x, list):
        return x
    elif isinstance(x, (str, dict)):
        return [x]
    else:
        raise TypeError(x)


class Instruction:
    def __init__(self, commands,
                 boundaries=[],
                 reader=''
                 ):
        self.commands = commands
        self.boundaries = boundaries
        self.reader = reader

    def select_applicable_boundaries(self, csv_rows: list):
        def is_found(rows, x):
            for row in rows:
                if row[0].startswith(x):
                    return True
            return False
        error_messages = ['Start or end boundary not found:']
        for boundary in self.boundaries:
            start = boundary['start']
            end = boundary['end']
            flag2 = False
            flag1 = is_found(csv_rows, start)
            if flag1:
                flag2 = is_found(csv_rows, end)
            if flag2 and flag1:
                return start, end
            error_messages.append(start)
            error_messages.append(end)
        raise ValueError('\n'.join(error_messages))

    @property
    def headers_dict(self):
        return {com['var']: iterate(com['header']) for com in self.commands}

    @property
    def required(self):
        return {com['var']: iterate(com['unit']) for com in self.commands}

    def required_pairs(self):
        return {(name, unit) for name, units in self.required.items()
                for unit in units}


def from_yaml(yaml_text: str):
    return list(yaml.load_all(yaml_text))


def yaml_to_instructions(yaml_doc: str):
    return [Instruction(**i) for i in yaml.load_all(yaml_doc)]


class InstructionSet:
    def __init__(self, yaml_doc: str):
        self.definitions = yaml_to_instructions(yaml_doc)

    @property
    def default(self):
        default_definition = [d for d in self.definitions if not d.boundaries]
        assert len(default_definition) == 1
        return default_definition[0]

    @property
    def by_segment(self):
        return [d for d in self.definitions if d.boundaries]


if __name__ == '__main__':
    from inputs import YAML_DOC
    d = yaml_to_instructions(YAML_DOC)
