"""Parsing parameters used to extract variables from raw CSV.

*Definition* class holds main and segment parsing instructions.

*Instruction* holds csv segment boundaries, parsing commands, units of measurement and optional name of a reader function.

Definition().tables property uses csv2df.parser.extract_tables() function.

"""

from kep.csv2df.parser import Segment
from kep.csv2df.row_model import Row
from kep.csv2df.reader import Popper
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
        self._markers = as_list(boundaries)

    def get_bounds(self, rows):
        """Get start and end line, which can be found in *rows*.

        Returns:
            start, end - tuple of start and end strings found in *rows*

        Raises:
            ValueError: no start/end line pairs was found in *rows*.

        """
        rows = list(rows)
        for marker in self._markers:
            s = marker['start']
            e = marker['end']
            if self._is_found(s, rows) and self._is_found(e, rows):
                return s, e
        self._raise_error(rows)

    @staticmethod
    def _is_found(line: str, rows: list):
        """
        Return:
           True, if *line* found at start of *rows[0]*
           False otherwise
        """
        if not isinstance(rows, list):
            raise TypeError(rows)
        for row in rows:
            r = Row(row)
            if r.startswith(line):
                return True
        return False

    def _raise_error(self, rows):
        """Prepare error message with diagnostics.

        Returns:
            string with message text
        """
        msg = []
        msg.append('start or end line marker not found')
        for marker in self._markers:
            s = marker['start']
            e = marker['end']
            msg.append('is_found: {} <{}>'.format(self._is_found(s, rows), s))
            msg.append('is_found: {} <{}>'.format(self._is_found(e, rows), e))
        raise ValueError('\n'.join(msg))

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
                required_labels unit(s) of measurement
                ex: 'bln_usd' or ['rog', 'rub']
        """
        self._varname = var
        self._header_strings = as_list(header)
        self._required_units = as_list(unit)

    @property
    def mapper(self):
        return {
            _header_string: self._varname for _header_string in self._header_strings}

    @property
    def required_labels(self):
        return [make_label(self._varname, unit)
                for unit in self._required_units]

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
