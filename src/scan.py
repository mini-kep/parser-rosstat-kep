from copy import copy
from collections import OrderedDict

from kep.util import iterate, load_yaml
from kep.dates import date_span
from kep.parser.reader import get_tables as read_tables
from kep.parser.units import UnitMapper
from kep.session.dataframes import unpack_dataframes
from locations import interim_csv

ALL_DATES = date_span('2009-04', '2018-06')       

# label assertion

def expected_labels(name, units):
    return [(name, unit) for unit in iterate(units)]

def raise_not_found(not_found_list, current_labels):
    msg = f'expected label(s) {not_found_list} not found in {current_labels}'
    raise AssertionError(msg)

def not_found(current_labels, name, units):
    expected_label_list = expected_labels(name, units)
    return [x for x in expected_label_list if x not in current_labels]

def assert_labels_found(tables, name, units):
    """Assert that labels defined by *name* and *units*
       are found in *tables*.
    """   
    current_labels = labels(parsed(tables)) 
    not_found_list = not_found(current_labels, name, units)
    if not_found_list:
        raise_not_found(not_found_list, current_labels)

# atomic parsing functions
    
def parse_units(tables, base_mapper):
    """Stage 1 of the table parsing algorithm."""
    for t in tables:
        for header in t.headers:
            unit = base_mapper.extract(header)
            if unit:
                t.unit = unit
    
def parse_headers(tables, name, headers):
    headers = iterate(headers)
    for t in tables:
        if t.contains_any(headers):
            t.name = name
            break
        
def assign_units(tables, units):
    unit = iterate(units)[0]
    for t in tables:
        t.unit = unit

def assign_format(tables, fmt):
    if fmt == 'fiscal':
        fmt = 'YA' + 'M' * 11
    for t in tables:
        t.row_format = fmt
        
def trail_down_names(tables, name, units):
    """Assign trailing variable names in tables.

      We look for a case where: 
      - a table name is defined once and 
      - there are following tables with expected unit тфьуы
      - but no variable name specified. 
      
      In this case we assign table name to previous table name.
    """
    _units = copy(iterate(units))
    trailing_allowed = False
    for i, table in enumerate(tables):
        if not _units:
            break
        if table.name == name:
            trailing_allowed = True
            if table.unit in _units:
                # unit already found, exclude it from futher search
                _units.remove(table.unit)
        condition = (i > 0 and
            trailing_allowed and
            table.name is None and
            table.unit in _units)        
        if condition:
            table.name = tables[i - 1].name
            _units.remove(table.unit)
            
 # limit scope 
           
def trim_start(tables, start_strings):
    """Drop tables before any of *start_strings*."""
    start_strings = iterate(start_strings)
    for i, t in enumerate(tables):
        if t.contains_any(start_strings):
            break
    return tables[i:]

def trim_end(tables, end_strings):
    """Drop tables after any of *end_strings*."""
    end_strings = iterate(end_strings)
    we_are_in_segment = True
    for i, t in enumerate(tables):
        if t.contains_any(end_strings):
            we_are_in_segment = False
        if not we_are_in_segment:
            break
    return tables[:i]      

# reference functions

def varcount(tables):
    return len(names(tables))

def underscore(label: tuple):
    name, unit = label 
    return f"{name}_{unit}"

def names(tables):
    res = []
    for t in tables:
        if t.name not in res:
            res.append(t.name)
    return res   

def labels(tables):
    return [(t.name, t.unit) for t in tables] 

def parsed(tables):
    return [t for t in tables if t]

def select(tables, name):
    return [t for t in tables if t.name==name]

def find(tables, string):
   for t in tables:
        if t.contains_any([string]):
            return t 
        
def datapoints(tables):
    """Return a list of values from parsed tables."""
    return [x for t in parsed(tables) for x in t.emit_datapoints()]

def dataframes(tables):
    """Return a tuple of annual, quarterly and monthly dataframes
       from parsed tables."""
    dfa, dfq, dfm = unpack_dataframes(datapoints(tables))
    return dfa, dfq, dfm        
        

# get parameters and data from filepaths

def get_parsing_parameters(filepath):
    return _get_common(filepath), _get_segments(filepath) 

def _read_parameters(filepath, pivot_key):
    """Read dictionaries from YAML file if *pivot_key* is there."""
    return [x for x in load_yaml(filepath) if pivot_key in x.keys()]

def _get_common(filepath):
    return _read_parameters(filepath, 'name')

def _get_segments(filepath):
    return _read_parameters(filepath, 'start_with')    

def get_unit_mapper(filepath):
    return UnitMapper(load_yaml(filepath)[0])

def get_tables(year, month):
    path = interim_csv(year, month)
    return read_tables(path)

# parsing batch functions

def parse_after_units(tables, 
                      name, 
                      headers, 
                      units, 
                      force_units=False, 
                      row_format=None,
                      mandatory=True):
    """Assign variable names to *tables* and perform optional mappings.    
       This is Stage 2 of the table parsing algorithm.
       All function arguments except *tables* are keys in YAML dictionaries.
    """
    parse_headers(tables, name, headers)
    trail_down_names(tables, name, units)
    if force_units:
        assign_units(tables, units)
    if row_format:
        assign_format(tables, row_format)
    if mandatory:        
        assert_labels_found(tables, name, units)

def apply_commands(tables, dicts):
    for d in dicts:
          parse_after_units(tables, **d)
    return tables      
    

def parse_common(tables, common_dicts, base_mapper):
    """Parse *tables* without cutting a segment of them."""
    # stage 1 - define units in tables
    parse_units(tables, base_mapper)      
    # stage 2 - define headers and other mapping 
    tables = apply_commands(tables, common_dicts)
    return parsed(tables)

def parse_segment(tables, start_with, end_with, commands):    
    """Trim and parse *tables*.
    
    Args:
      _tables - list Talble instances  
      start_with, end_with are lists of strings
      commands - list of dictionaries.      
    
    All args except tables are dictionary keys in a YAML file.
    """
    # note: did not work out as inline functions, using assignments
    tables = trim_start(tables, start_with)
    tables = trim_end(tables, end_with)
    tables = apply_commands(tables, commands)
    return parsed(tables)       

def get_parsed_tables(tables, 
                      common_dicts, 
                      segment_dicts,
                      base_mapper):    
    parse_units(tables, base_mapper)
    parsed_tables = parse_common(tables, common_dicts, base_mapper)       
    for sd in segment_dicts:
        # make a copy, otherwise we will sploil the next run of function
        tables2 = copy(tables)
        new_tables = parse_segment(tables2, **sd)
        parsed_tables.extend(new_tables)
    return parsed_tables    

def main(common_dicts, segment_dicts, base_mapper):
    """Run parsing for all dates and return latest set of tables."""
    for year, month in ALL_DATES:
        print(year, month)
        tables = get_tables(year, month)
        last = get_parsed_tables(tables, common_dicts, segment_dicts,  base_mapper)
    return last    

# batch reference     
def get_groups(filepath):
    def _first_key(d):
        return tuple(d)[0]
    items = load_yaml(filepath)[0]  
    groups = [(_first_key(x), x[_first_key(x)]) for x in items]
    return OrderedDict(groups)

class Grouper:
    def __init__(self, filepath):
        self.groups = get_groups(filepath)
    
    @property
    def names(self):
        return set([x for _names in self.groups.values() for x in _names])
    
    def items(self):
        return self.groups.items()
    
    def minus(self, x):
        return list(self.names - set(x))    

    def outside(self, x):
        return list(set(x) - self.names)
    
    def includes_too_much(self, x):        
        return 'Not found in data\n    %s' % with_comma(self.minus(x))

    def includes_too_little(self, x):
        return 'Not listed in groups\n    %s' % with_comma(self.outside(x))  

GROUPER = Grouper('param//groups.yml')

def filtered_labels(label_list, name):
    labels = [(name, unit) for _name, unit in label_list if _name == name] 
    return list(map(underscore, labels))

def with_comma(items):
    return ", ".join(items)
    
def print_reference(tables, grouper = GROUPER):
    print(varcount(tables), "variables and", len(tables), "labels")
    label_list = labels(tables)
    name_list = names(tables)
    found = []
    for group, group_names in grouper.items():
        print(group)
        for name in group_names:            
            if name in name_list:
                found.append(name)  
                group_labels = filtered_labels(label_list, name)
                msg = with_comma(group_labels)            
                print("    {} ({})".format(name, msg))           
    if grouper.minus(found):
        print(grouper.includes_too_much(found))
    if grouper.outside(found): 
        print(grouper.includes_too_little(found))

if __name__ == '__main__':
    common_dicts, segment_dicts = get_parsing_parameters('param//instructions.yml') 
    base_mapper = get_unit_mapper('param//base_units.yml')
    tables = main(common_dicts, segment_dicts, base_mapper)  
    values = datapoints(tables)
    print_reference(tables)
    
    from fax import validate, get_checkpoints
    mandatory, optional = get_checkpoints('param//checkpoints.yml')
    validate(values, mandatory, optional)
    
    