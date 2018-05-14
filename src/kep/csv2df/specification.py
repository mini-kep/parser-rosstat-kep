"""Parsing parameters used to extract variables from raw CSV.
"""
from typing import List

from kep.csv2df.parser import Segment
from kep.csv2df.row_model import Row
from kep.csv2df.reader import Popper
from kep.csv2df.util.label import make_label

from kep.parsing_definition import PARSING_DEFINITIONS, UNITS

class Boundary():
    def __init__(self, line, rows, name='boundary'):
        self.is_found = self._find(line, rows)
        self._name = name
        self._line = line
        
    @staticmethod    
    def _find(line: str, rows:  List[str]):                
       for row in rows:
            if Row(row).startswith(line):
                return True  
       return False
   
    def __str__(self):
        def shorten(string):
            tab = 10 
            if len(string) > tab:
                s = string[:tab] + '...'
            else:
                s = string
            return  f'\'{s}\''
        line = shorten(self._line)
        result = {True:'', False:'not'}[self.is_found]        
        return f'{self._name} line {result} found: {line}'       

b1 = Boundary('a', ['a', 'b', 'k', 'zzz'])
assert b1.is_found is True  

b2 = Boundary('hm!', ['a', 'b', 'k', 'zzz'])
assert b2.is_found is False
      

class Partition:   
    def __init__(self, start: str, end: str, rows: List[str]):
        self.start = Boundary(start, rows, 'start')
        self.end = Boundary(end, rows, 'end')
        self.lines_count = len(rows)

    @property        
    def is_matched(self) -> bool:
        return self.start.is_found and self.end.is_found
    
    def __str__(self):
        msg = [str(self.start), 
               str(self.end), 
               f'Total of {self.lines_count} rows']
        return '\n'.join(msg)


p = Partition('a', 'k', ['a', 'b', 'k', 'zzz'])
assert p.is_matched is True
assert 'Total of 4 rows' in str(p)
   

class Scope():
    """Delimit start and end line for CSV fragment using several lines.

       Holds several versions of start and end line, returns applicable lines
       for a particular CSV. This solves problem of different
       headers for same table at various data releases.
    """
    def __init__(self, boundaries: List[dict]):
        self.markers = boundaries
        
    def get_bounds(self, rows: List[str]):
        """Get start and end line, which is found in *rows* list of strings.
        Returns:
            start, end - tuple of start and end strings found in *rows*
        Raises:
            ValueError: no start/end line pairs was found in *rows*.
        """
        for m in self.markers:
            partition = Partition(m['start'], m['end'], rows)
            if partition.is_matched:
                return partition.start, partition.end
        self._raise_error(rows)

    def _raise_error(self, rows):
        """Prepare error message with diagnostics.
        Raises:
            ValueError with message string
        """
        msg = ['Start or end boundary not found:']
        for m in self.markers:
            partition = Partition(m['start'], m['end'], rows)
            msg.extend(str(partition.start))
            msg.extend(str(partition.end))
        raise ValueError('\n'.join(msg))

    def __repr__(self):
        return self.markers.__repr__()


sc = Scope(dict(start='a', end='k'))
assert 'a', 'k' == sc.get_bounds(['a', 'b', 'k', 'zzz'])


class ParsingCommand():
    def __init__(self, varname, header_strings, required_units):
        """Create parsing instructions for an individual variable.

        Args:
            var (str):
                varaible name, ex: 'GDP'
            headers (str or list of strings):
                header string(s) associated with variable names
                ex: 'Oбъем ВВП' or ['Oбъем ВВП', 'Индекс физического объема произведенного ВВП']
            units (str or list):
                required_labels unit(s) of measurement
                ex: 'bln_usd' or ['rog', 'rub']
        """
        self._varname = varname
        self._header_strings = header_strings
        self._required_units = required_units

    @property
    def mapper(self):
        return {h: self._varname for h in self._header_strings}

    @property
    def required_labels(self):
        return [make_label(self._varname, unit) for unit in self.units]

    @property
    def units(self):
        return self._required_units


class Definition(object):
    """Holds together:
        - parsing commands
        - units dictionary
        - (optional) defintion scope
        - (optional) custom reader function name

       Properties:
         - mapper (dict)
         - required_labels (list)
         - units (dict)
         - reader (str)
         - scope(Scope)

       Public method:
         - get_bounds()
         - .values
    """

    def __init__(self, commands, boundaries, reader):
        self.commands = [ParsingCommand(**c) for c in commands]
        self.units = UNITS
        self.scope = Scope(boundaries)
        self.reader = reader

    @property
    def mapper(self):
        d = {}
        for c in self.commands:
            d.update(c.mapper)
        return d

    @property
    def required_labels(self):
        return [r for c in self.commands for r in c.required_labels]

    def get_bounds(self, rows):
        return self.scope.get_bounds(rows)

    @property
    def values(self):
        return Segment(self.rows, self).values 


class Specification:
    """Main parsing definition and instructions by segment."""

    def __init__(self, definition_dict_list):
        first_dict = definition_dict_list[0]
        self.definitions = [Definition(**first_dict)]
        for definition_dict in definition_dict_list[1:]:
            self.append(**definition_dict)
        self.units = UNITS

    def append(self, commands, boundaries, reader):
        pdef = Definition(commands, boundaries, reader)
        self.definitions.append(pdef)

    @property
    def definition_default(self):
        return self.definitions[0]

    @property
    def definition_segments(self):
        return self.definitions[1:]

    def attach_data(self, csv_text: str):
        """Break *csv_text* into segments using self.segments boundaries.
        Converts to *csv_text* string to list of lists of strings.
        """
        stack = Popper(csv_text)
        for pdef in self.defintions[1:]:
            start, end = pdef.get_bounds(stack.rows)
            pdef.rows = stack.pop(start, end)
        self.defintions[0].rows = stack.remaining_rows()

    @property
    def values(self):
        return [v for pdef in self.definitions for v in pdef.values]

# WARNING: a singleton?
SPEC = Specification(PARSING_DEFINITIONS)