from copy import copy
from kep.units import UnitMapper
from kep.util import iterate
from kep.commands import extract_parameters, extract_labels
from kep.verifier import require_all, require_any

__all__ = ['Worker', 'make_parser']


class Worker:
    """Parse *tables* using *base_mapper* and .apply(command). 
   
    Limit scope of tables: 
       
        - start_with
        - end_with   
    
    Parse tables:
        
        - name
        - headers
        - units

    Handle special situaltions:

        - force_units
        - force_format
        - trail_down_names
       
    All methods above are valid parsing commands in yaml file.    
    """
    def __init__(self, tables, base_mapper: UnitMapper):
        self.tables = tables
        self.base_mapper = base_mapper
        self.name = None
        self.parse_units()
        
    def new(self):
        """Create a copy of this instance."""        
        return copy(self)
    
    def apply(self, command):
        """Run a *command* on itself."""
        method, arg = extract_parameters(command)
        func = getattr(self, method)
        if arg:
            func(arg)
        else:
            func()

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
           Works after .var().
        """
        if self.name is None:
            raise ValueError('Variable name not defined.')
        headers = iterate(headers)
        for t in self.tables:
            if t.contains_any(headers):
                t.name = self.name
                # speedup: look for first entry only
                break

    def units(self, units):
        """Set list of *units* for parsing."""
        self.units = iterate(units)

    def parse_units(self):
        """Identify units using standard units mapper."""
        for i, t in enumerate(self.tables):
            for header in t.headers:
                unit = self.base_mapper.extract(header)
                if unit:
                    t.unit = unit
                    
    def force_units(self, unit: str):
        """All tables in segment will be assigned this *unit* of measurement. 
        """
        for t in self.tables:
            t.unit = unit

    def force_format(self, fmt: str):
        """Row format for tabels will be assigned to *fmt*."""
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
        
           We look for a case where a table name is defined once and there are 
           following tables with expected unit names, but no variable name 
           specified. 
           
           In this case we assign table name similar to previous table. 
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

    def all(self, strings):
        """Require all values from strings, raise exception otherwise."""
        require_all(strings, self.datapoints())
        
    def any(self, strings):
        """Require at least one value from strings, raise exception otherwise."""
        require_any(strings, self.datapoints())
        
    def datapoints(self):
        """Values in parsed tables.
        
        Return:
            list of Datapoint instances"""
        return [x for t in self.parsed_tables for x in t.emit_datapoints()]
   
    @property
    def parsed_tables(self):
        return [t for t in self.tables if t] 


def get_parsed_tables(tables, base_mapper, methods):
    worker = Worker(tables, base_mapper)
    for method in methods:
        worker.apply(method)
    return worker.parsed_tables


def check_labels(parsed_tables, expected_labels):
    labels = [t.label for t in parsed_tables if t]
    if labels != expected_labels:
        import pdb; pdb.set_trace()
        raise AssertionError(labels, expected_labels)


def make_parser(base_mapper):
    def wrapper(tables, commands):
        expected_labels = extract_labels(commands)
        parsed_tables = get_parsed_tables(tables, base_mapper, commands)
        check_labels(parsed_tables, expected_labels)
        return parsed_tables             
    return wrapper       

