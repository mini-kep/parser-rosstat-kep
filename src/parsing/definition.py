"""Parsing definition to identify tables in the data source file.

   A defnition contains a list of nested dicts.

   Each dict has following keys:
   - commands, a list of dicts each with following keys:
       - variable name ('GDP')
       - corresponding headers ('Oбъем ВВП')
       - units of measurement ('bln_rub')
   - boundaries (start and end lines of text)
   - reader function name(string)

Create parsing instructions for an individual variable.

    Keys:
        varname (str):
            varaible name, ex: 'GDP'
        table_headers-strings (list of strings):
            header string(s) associated with variable names
            ex: ['Oбъем ВВП'] or ['Oбъем ВВП', 'Индекс физического объема произведенного ВВП']
        units (list of strings):
            required_labels unit(s) of measurement
            ex: ['bln_usd]' or ['rog', 'rub']
"""

import yaml

from parsing.csv_reader import is_identical
from parsing.label import make_label


def iterate(x):
    if isinstance(x, list):
        return x
    elif isinstance(x, (str, dict)):
        return [x]
    else:
        raise TypeError(x)


class Definition:
    def __init__(self, units,
                 commands,
                 boundaries=[],
                 reader=''
                 ):
        self.units = units
        # transform commands
        self.mapper = self.make_mapper_dict_for_table_headers(commands)
        self.required_labels = self.make_required_labels(commands)
        # attach as is
        self.boundaries = boundaries
        self.reader = reader

    @staticmethod
    def make_mapper_dict_for_table_headers(commands):
        result = {}
        for command in iterate(commands):
            for header in iterate(command['header']):
                result[header] = command['var']
        return result

    @staticmethod
    def make_required_labels(commands):
        result = []
        for command in iterate(commands):
            for unit in iterate(command['unit']):
                result.append(make_label(command['var'], unit))
        return result

    def select_applicable_boundaries(self,
                                     csv_rows: list,
                                     is_identical=is_identical):
        def is_found(rows, x):
            for row in rows:
                if is_identical(row[0], x):
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
            error_messages.append(start[:20])
            error_messages.append(end[:20])
        raise ValueError('\n'.join(error_messages))


def from_yaml(yaml_text: str):
    return list(yaml.load_all(yaml_text))


def create_definitions(units: dict, yaml_text: str):
    instructions_by_segment = from_yaml((yaml_text))
    return [Definition(units=units, **instruction_set)
            for instruction_set in instructions_by_segment]
