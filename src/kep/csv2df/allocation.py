"""Create units of work that contain data and parsing parameters.

    yield_parsing_assingments(...)

"""
from typing import List
from collections import namedtuple

from kep.csv2df.row_model import Row
from kep.csv2df.reader import Popper


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
            return  f'<{string[:10]}...>'
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

Assignment = namedtuple('Assignment', 
                        ['mapper', 'required_labels', 'units', 'reader', 'rows']) 

def make_assignment(rows, def_dict, units):
    return Assignment(mapper = def_dict['mapper'],
                      required_labels = def_dict['required_labels'],
                      reader = def_dict['reader'],
                      units = units,
                      rows = rows)

def yield_parsing_assingments(csv_text: str, definition_dicts, units):    
    def factory(def_dict, rows):
        return make_assignment(rows, def_dict, units)              
    stack = Popper(csv_text)
    for def_dict in definition_dicts[1:]:
        start, end = get_boundaries(def_dict['boundaries'], stack.rows)
        yield factory(def_dict, rows=stack.pop(start, end))
    yield factory(definition_dicts[0], rows=stack.remaining_rows())

