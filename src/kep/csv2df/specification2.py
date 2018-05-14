"""Parsing parameters used to extract variables from raw CSV.

*Definition* class holds main and segment parsing instructions.

*Instruction* holds csv segment boundaries, parsing commands, units of measurement and optional name of a reader function.

Definition().tables property uses csv2df.parser.extract_tables() function.

"""

from kep.csv2df.parser import Segment
from kep.csv2df.row_model import Row
from kep.csv2df.reader import Popper
from kep.csv2df.util.label import make_label

from typing import List, Union


def as_list(x):
    """Transform *x* to list *[x]*.

       Returns:
           list
    """
    if isinstance(x, list):
        return x
    elif isinstance(x, tuple):
        return list(x)
    else:
        return [x]


class Boundary():
    def __init__(self, line, rows, name='boundary'):
        self._is_found = self._find(line, rows)
        self._name = name
        self._line = line
        
    def is_found(self):    
        return self._is_found

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
        result = {True:'found', False:'not found'}[self._is_found]        
        return f'{self._name} line {result}: {line}'       

b1 = Boundary('a', ['a', 'b', 'k', 'zzz'])
assert b1.is_found() is True  

b2 = Boundary('hm!', ['a', 'b', 'k', 'zzz'])
assert b2.is_found() is False
      

class Partition:   
    def __init__(self, start: str, end: str, rows: List[str]):
        self.start = Boundary(start, rows, 'start')
        self.end = Boundary(end, rows, 'end')
        self.lines_count = len(rows)

    @property        
    def is_matched(self) -> bool:
        return self.start.is_found() and self.end.is_found()
    
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
    def __init__(self, boundaries: Union[dict, List[dict]]):
        self.markers = as_list(boundaries)        
        
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
    def __init__(self, var, header, unit):
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
        self._varname = var
        self._header_strings = as_list(header)
        self._required_units = as_list(unit)

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
    """

    def __init__(self, commands, units, boundaries=None, reader=None):
        self.commands = [ParsingCommand(**c) for c in as_list(commands)]
        self.units = units
        self.rows = []
        if boundaries:
            self.scope = Scope(boundaries)
        else:
            self.scope = None
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

    def __init__(self, commands, units):
        self.default = Definition(commands=commands, units=units)
        self.segments = []
        # these units will be used in all of the parsing
        self.units = units

    def append(self, commands, boundaries, reader=None):
        pdef = Definition(
            commands=commands,
            units=self.units,
            boundaries=boundaries,
            reader=reader)
        self.segments.append(pdef)

    def attach_data(self, csv_text: str):
        """Break *csv_text* into segments using self.segments boundaries.
        Converts to *csv_text* string to list of lists of strings.
        """
        stack = Popper(csv_text)
        for pdef in self.segments:
            start, end = pdef.get_bounds(stack.rows)
            pdef.rows = stack.pop(start, end)
        self.default.rows = stack.remaining_rows()

    @property
    def definitions(self):
        return [self.default] + self.segments

    @property
    def values(self):
        return [v for pdef in self.definitions for v in pdef.values]

def create_specification(default_commands, default_units):
    return Specification(default_commands, default_units)
