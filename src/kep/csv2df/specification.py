"""Parsing parameters used to extract variables from raw CSV.
"""
from typing import List

from kep.csv2df.parser import get_values
from kep.csv2df.row_model import Row
from kep.csv2df.reader import Popper
from kep.csv2df.util.label import make_label

from kep.parsing_definition import PARSING_DEFINITIONS, UNITS

class Boundary():
    def __init__(self, line, rows, name='boundary'):
        self.is_found = self._find(line, rows)
        self._name = name
        self._line = line
        
    def text(self):
        return self._line        
        
    @staticmethod    
    def _find(line: str, rows:  List[str]):                
       for row in rows:
            if Row(row).startswith(line):
                return True  
       return False
   
    def __str__(self):
        def shorten(string):
            tab = 10 
            return  f'<{string[:tab]}...>'
        result = {True:'found:  ', False:'NOT found:'}[self.is_found]        
        return f'{self._name} line {result} {shorten(self._line)}' 

class Start(Boundary):
      def __init__(self, line, rows):
          super().__init__(line, rows, "Start")

class End(Boundary):
      def __init__(self, line, rows):
          super().__init__(line, rows, "End")
      

b1 = Boundary('a', ['a', 'b', 'k', 'zzz'])
assert b1.is_found is True  

b2 = Boundary('hm!', ['a', 'b', 'k', 'zzz'])
assert b2.is_found is False
      

class Partition:   
    def __init__(self, start: str, end: str, rows: List[List[str]]):
        self.start = Start(start, rows)
        self.end = End(end, rows)
        self.lines_count = len(rows)

    def is_matched(self) -> bool:
        return self.start.is_found and self.end.is_found    

    def __str__(self):
        msg = [str(self.start), 
               str(self.end), 
               f'Total of {self.lines_count} rows']
        return '\n'.join(msg)


p = Partition('a', 'k', ['a', 'b', 'k', 'zzz'])
assert p.is_matched() is True
assert 'Total of 4 rows' in str(p)
   

def get_boundaries(boundaries: List[dict], rows: List[str]):
    """Get start and end line, which is found in *rows* list of strings.
    
    Returns:
        start, end - tuple of start and end strings found in *rows*
    Raises:
        ValueError: no start/end line pairs was found in *rows*.
    """
    error_message = ['Start or end boundary not found:']
    for m in boundaries:
        partition = Partition(start=m['start'], end=m['end'], rows=rows)
        s, e = partition.start, partition.end
        if partition.is_matched():
            return s.text(), e.text() 
        error_message.extend([str(s), str(e)])
    raise ValueError('\n'.join(error_message))    
        


r1 = get_boundaries ([dict(start='a', end='k'), dict(start='a', end='g1')],
                     [['a'], ['b'], ['g12345'], ['zzz']])
assert r1

# TEST: results in rrror
#get_boundaries ([dict(start='a', end='k'), dict(start='a', end='g1')],
#                     [['a'], ['b'], ['EEE'], ['zzz']])


class ParsingCommand():
    def __init__(self, varname: str, 
                       table_headers: List[str], 
                       required_units: List[str]):
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
        self._header_strings = table_headers
        self._required_units = required_units

    @property
    def mapper(self):
        return {header_str: self._varname for header_str in self._header_strings}

    @property
    def required_labels(self):
        return [make_label(self._varname, unit) for unit in self.units]

    @property
    def units(self):
        return self._required_units
    

class Definition(object):
    """Holds together:
        - parsing commands
        - global units mapper dictionary
        - (optional) definition scope
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
    def __init__(self, commands: List[dict], 
                       boundaries: List[dict], 
                       reader: str):
        self.commands = [ParsingCommand(**c) for c in commands]
        self.units = UNITS
        self.boundaries = boundaries
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
        return get_boundaries(self.boundaries, rows)
    
    @property
    def values(self):
        return get_values(self.rows, self)
    
    def __repr__(self):
        return str(self.mapper)


class Specification:
    """Main parsing definition and instructions by segment."""

    def __init__(self, definition_dicts):
        self.definitions = []        
        for definition_dict in definition_dicts:
            pdef = Definition(**definition_dict)
            self.definitions.append(pdef)
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
        for pdef in self.definitions[1:]:
            start, end = pdef.get_bounds(stack.rows)
            pdef.rows = stack.pop(start, end)
        self.definitions[0].rows = stack.remaining_rows()

    @property
    def values(self):
        return [v for pdef in self.definitions for v in pdef.values]
    

# WARNING: a singleton?
PARSING_SPECIFICATION = Specification(PARSING_DEFINITIONS)

# EXPERIMENTAL:
    
def yield_parsing_assingments(definition_dicts: list, csv_text: str):
    stack = Popper(csv_text)
    for def_dict in definition_dicts[1:]:
        start, end = get_boundaries(def_dict['boundaries'], stack.rows)
        yield make_assignment(def_dict, 
                              rows=stack.pop(start, end))
    yield make_assignment(definition_dicts[0], 
                          rows=stack.remaining_rows())
    
from collections import namedtuple
Assignment = namedtuple('Assignment', 
                        ['mapper', 'required_labels', 'units', 'reader', 'rows']) 

def make_assignment(def_dict, rows):
    return Assignment(mapper=def_dict['mapper'],
                      required_labels=def_dict['required_labels'],
                      reader=def_dict['reader'],
                      units = UNITS,
                      rows = rows)
    
    
