from copy import copy
from kep.units import UnitMapper
from kep.util import iterate
from kep.reader import import_tables_from_string
from kep.row import Datapoint

__all__ = ['Worker', 'Container']

class Worker:
    """Parse *tables* using commands below.
    
    Methods
    =======
    
    Limit scope of tables using: 
       
        - start_with
        - end_with   
    
    Parse tables using:
        
        - name
        - headers
        - units

    Handle special situaltions using:

        - force_units
        - force_format
        - trail_down_names
       
    All methods are valid parsing commands in yaml file.    
    """
    def __init__(self, tables, base_mapper: UnitMapper):
        self.tables = tables
        self.name = None
        self.base_mapper = base_mapper

    def start_with(self, start_strings):
        """Limit parsing segment starting from any of *start_strings*."""
        start_strings = iterate(start_strings)
        for i, t in enumerate(self.tables):
            if t.contains_any(start_strings):
                break
        self.tables = self.tables[i:]
        return self

    def end_with(self, end_strings):
        """Limit parsing segment ending by any of *end_strings*."""
        end_strings = iterate(end_strings)
        we_are_in_segment = True
        for i, t in enumerate(self.tables):
            if t.contains_any(end_strings):
                we_are_in_segment = False
            if not we_are_in_segment:
                break
        self.tables = self.tables[:i]
        return self

    def var(self, name: str):
        """Set current variable *name* for parsing."""
        self.name = name

    def headers(self, headers):
        """Set *headers* strings corresponding to variable *name*.
           Works after set_name().
        """
        if self.name is None:
            raise ValueError('Variable name not defined.')
        headers = iterate(headers)
        for t in self.tables:
            if t.contains_any(headers):
                t.name = self.name
        return self

    def units(self, units):
        """Set list of *units* for parsing."""
        self.units = iterate(units)
        self._parse_units()

    def _parse_units(self):
        """Identify units using standard units mapper."""
        for i, t in enumerate(self.tables):
            for header in t.headers:
                unit = self.base_mapper.extract(header)
                if unit:
                    t.unit = unit

    # TODO
#    def parse_units_with(self, mapper: dict={}):
#        for t in self.tables:
#            pass
#        return self

    def force_units(self, unit):
        """All tables in segment will be assigned 
           this *unit* of measurement. 
        """
        for t in self.tables:
            t.unit = unit

    def force_format(self, fmt: str):
        if fmt == 'fiscal':
            fmt = 'YA' + 'M' * 11
        for t in self.tables:
            t.row_format = fmt
        



#TODO
#    def trail_down_units(self):
#        """
#        """
##        for prev_table, table in self.prev_next_pairs():
##            if (table.unit is None
##                and prev_table.unit is not None
##                and table.name):
##                table.unit = prev_table.unit
#        pass

    def trail_down_names(self):
        """Assign trailing variable names in tables.
        
           We look for a situation where table name is defined once
           and there are following tables with expected unit names, but no
           variable name specified. 
           
           In this case we assign table variable name similar to previous 
           table. 
        """
        _units = copy(self.units)
        trailing_allowed = False
        for i, table in enumerate(self.tables):
            if not _units:
                break
            if table.name == self.name:
                trailing_allowed = True
                if table.unit in _units:
                    # unit already found, exclude it from futher search 
                    _units.remove(table.unit)
            if (i > 0 and 
                trailing_allowed and 
                table.name is None and 
                table.unit in _units):
                # then
                table.name = self.tables[i-1].name
                _units.remove(table.unit)

    def require(self, strings):
        _datapoints = self.datapoints()
        for string in iterate(strings):
            label, freq, date, value = string.split(' ')
            value = float(value)
            dp = Datapoint(label, freq, date, value)
            if dp not in _datapoints:
                similar = [x for x in _datapoints if x.label == dp.label] 
                raise AssertionError((dp, similar))
        
    def datapoints(self):
        """Values in parsed tables."""
        return [x for t in self.tables 
                  for x in t.emit_datapoints()
                  if t]

    @property
    def labels(self):
        """Parsed variable names."""
        return [t.label for t in self.tables if t]

class Container:
    def __init__(self, csv_source: str, base_mapper: UnitMapper):
        self.incoming_tables = import_tables_from_string(csv_source)
        self.parsed_tables = []
        self.base_mapper = base_mapper
        self.worker = None

    def init(self):
        self.worker = Worker(self.incoming_tables, self.base_mapper)

    def push(self):
        current_parsed_tables = [t for t in self.worker.tables if t]
        self.parsed_tables.extend(current_parsed_tables)

    def apply(self, command_functions):
        self.init()
        for func in command_functions:
            func(self.worker)
        self.push()

    def check(self, expected_labels):
        if self.worker.labels != expected_labels:
            raise AssertionError(self.worker.labels, expected_labels)

    def datapoints(self):
        return list(self.emit_datapoints())

    def emit_datapoints(self):
        for t in self.parsed_tables:
            for x in t.emit_datapoints():
                yield x

    @property
    def labels(self):
        return [t.label for t in self.parsed_tables]

