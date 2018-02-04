"""

"""

from kep.csv2df.parser import extract_tables
from kep.csv2df.row_model import Row
from kep.csv2df.row_stack import Popper
from kep.csv2df.util.label import make_label


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


class Scope():
    """Delimit start and end line in CSV file.

       Holds several versions of start and end line, returns applicable lines
       for a particular CSV. This solves problem of different
       headers for same table at various data releases.       
           
       #We parse CSV file by segment, because some table headers repeat themselves in
       #CSV file. Extracting a piece out of CSV file gives a good isolated input for parsing.

    """
    def __init__(self, boundaries):
        self.__markers = as_list(boundaries)

    def get_bounds(self, rows):
        """Get start and end line, which can be found in *rows*.

        Returns:
            start, end - tuple of start and end strings found in *rows*

        Raises:
            ValueError: no start/end line pairs was found in *rows*.

        """
        rows = list(rows)
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            if self._is_found(s, rows) and self._is_found(e, rows):
                return s, e
        msg = self._error_message(rows)
        raise ValueError(msg)

    @staticmethod
    def _is_found(line, rows):
        """
        Return:
           True, if *line* found at start of some entry in *rows*
           False otherwise
        """
        for row in rows:
            if Row(row).startswith(line):
                return True
        return False

    def _error_message(self, rows):
        """Prepare error message with diagnostics.

        Returns:
            string with message text
        """
        msg = []
        msg.append('start or end line marker not found')
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            msg.append('is_found: {} <{}>'.format(self._is_found(s, rows), s))
            msg.append('is_found: {} <{}>'.format(self._is_found(e, rows), e))
        return '\n'.join(msg)

    def __str__(self):  # possible misuse of special method consider using __str__
        s = self.__markers[0]['start'][:10]
        e = self.__markers[0]['end'][:10]
        return 'bound by start <{}...> and end <{}...>'.format(s, e)


class ParsingCommand():
    def __init__(self, var, header, unit, check=None):
        """Create parsing instructions for an individual variable.

        Args:
            var (str):
                varaible name, ex: 'GDP'
            headers (str or list of strings):
                header string(s) associated with variable names
                ex: 'Oбъем ВВП' or ['Oбъем ВВП', 'Индекс физического объема произведенного ВВП']
            units (str or list):
                required unit(s) of measurement
                ex: 'bln_usd' or ['rog', 'rub']
        """
        self._varname = var
        self._header_strings = as_list(header)
        self._required_units = as_list(unit)

    @property
    def mapper(self):
        return {hs: self._varname for hs in self._header_strings}

    @property
    def required(self):
        return list(make_label(self._varname, unit)
                    for unit in self._required_units)

    @property
    def units(self):
        return self._required_units


class Def(object):
    """Holds together:
        - parsing commands
        - units dictionary
        - (optional) defintion scope
        - (optional) custom reader function name        

       Properties:
           - mapper (dict)
           - required (list)
           - units (dict)
           - reader (str)
           - scope(Scope)

       Public method:
            - get_bounds()
    """

    def __init__(self, commands, units, boundaries=None, reader=None):
        # FIXME: 
        #if not commands or not units:
        #    raise ValueError
        self.commands = [ParsingCommand(**c) for c in as_list(commands)]
        self.units = units
        self.csv_segment = ''
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
    def required(self):
        return [r for c in self.commands for r in c.required]

    def get_bounds(self, rows):
        return self.scope.get_bounds(rows)

    @property 
    def tables(self):
        return extract_tables(self.csv_segment, self)


class Definition:
    def __init__(self, commands, units):
        self.default = Def(commands=commands, units=units)
        self.segments = []
        self.units = units

    def append(self, commands, boundaries, reader=None):         
        pdef = Def(commands, self.units, boundaries, reader) 
        self.segments.append(pdef)

    def attach_data(self, csv_text):
        """Yield CSV segments and corresponding parsing definitons.

        Yield CSV segments as Row() instances and corresponding
        parsing definitons based on *spec* parsing specification.

        Args:
            spec: parsing specification as spec.Specification() instance

        Yields:
            Parsing definiton with a *csv_segment* assigned. 
        """
        stack = Popper(csv_text) 
        for pdef in self.segments:
            start, end = pdef.get_bounds(stack.rows)
            pdef.csv_segment = stack.pop(start, end) 
        self.default.csv_segment = stack.remaining_rows()
        return self

    @property
    def tables(self):           
        pdefs = [self.default] + self.segments 
        return [t for pdef in pdefs for t in pdef.tables]
