from copy import copy
from collections import OrderedDict

from kep.util import iterate, load_yaml
from kep.dates import date_span
from kep.parser.reader import get_tables as read_tables
from kep.parser.units import UnitMapper
from kep.session.dataframes import unpack_dataframes
from locations import interim_csv

ALL_DATES = date_span('2009-04', '2018-06')       

# label assertions

def expected_labels(name, units):
    return [(name, unit) for unit in iterate(units)]

def message_not_found(expected_label, current_labels):
    return f'expected label {expected_label} not found in {current_labels}'

def assert_labels_found(tables, name, units):
    current_labels = labels(parsed(tables)) 
    expected_label_list = expected_labels(name, units)
    for lab in expected_label_list:
        if lab not in current_labels:
            msg = message_not_found(lab, current_labels)
            print(msg)
            #import pdb; pdb.set_trace()
            raise AssertionError(msg)            

# atomic parsing functions
    
def parse_units(tables, base_mapper):
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

      We look for a case where a table name is defined once and there are
      following tables with expected unit names, but no variable name
      specified. In this case we assign table name similar to previous table.
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
        if (i > 0 and
            trailing_allowed and
            table.name is None and
            table.unit in _units):
            # then
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

def underscore(name, unit):
    return f"{name}_{unit}"    

def names(tables):
    res = []    
    [res.append(t.name) for t in tables if t.name not in res]
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
        

# get parameters and data

def get_parsing_parameters(filepath):
    return get_common(filepath), get_segments(filepath) 

def read_parameters(filepath, pivot_key):
    return [x for x in load_yaml(filepath) if pivot_key in x.keys()]

def get_common(filepath):
    return read_parameters(filepath, 'name')

def get_segments(filepath):
    return read_parameters(filepath, 'start_with')    

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
    parse_headers(tables, name, headers)
    trail_down_names(tables, name, units)
    if force_units:
        assign_units(tables, units)
    if row_format:
        assign_format(tables, row_format)
    if mandatory:        
       assert_labels_found(tables, name, units)

def parse_common(tables, common_dicts, base_mapper):
    parse_units(tables, base_mapper)         
    for d in common_dicts:
          parse_after_units(tables, **d)
    return parsed(tables)

def parse_segment(tables, start_with, end_with, commands):
    tables = trim_start(tables, start_with)
    tables = trim_end(tables, end_with)
    for p in commands:
        parse_after_units(tables, **p)
    return parsed(tables)       

def get_parsed_tables(tables, 
                      common_dicts, 
                      segment_dicts,
                      base_mapper):    
    parse_units(tables, base_mapper)
    res = parse_common(tables, common_dicts, base_mapper)       
    for d in segment_dicts:
        _tables = copy(tables)     
        _res = parse_segment(_tables, **d)
        res.extend(_res)
    return res    

def main(common_dicts, segment_dicts, base_mapper):
    """Run parsing for all dates and return latest set of tables."""
    for year, month in ALL_DATES:
        print(year, month)
        tables = get_tables(year, month)
        last = get_parsed_tables(tables, common_dicts, segment_dicts,  base_mapper)
    return last    

# batch reference     
def get_groups(filepath):
    items = load_yaml(filepath)[0]  
    groups = [(first_key(x), x[first_key(x)]) for x in items]
    return OrderedDict(groups)

GROUPS = get_groups('groups.yml')

def with_comma(items):
    return ", ".join(items)
    
def print_reference(tables):    
    print(varcount(tables), "variables and", len(tables), "labels")
    label_list = labels(tables)
    name_list = names(tables)
    found = []
    for group, group_names in GROUPS.items():
        print(group)
        for name in group_names:            
            if name in name_list:
                found.append(name)  
                labels_for_name = [underscore(name, unit) 
                                   for _name, unit in label_list
                                   if _name == name]
                msg = with_comma(labels_for_name)                                    
                print(f"    {name} ({msg})")           
    group_names = [x for _names in GROUPS.values() for x in _names]
    nf = set(group_names) - set(found)
    if nf:
        print('\nNot found in data\n   ', with_comma(nf))
    ng = set(name_list) - set(group_names)
    if ng: 
        print('\nNot listed in groups\n   ', with_comma(ng))   
                  

def first_key(d):
    return list(d.keys())[0]

if __name__ == '__main__':
    common_dicts, segment_dicts = get_parsing_parameters('instructions.yml') 
    base_mapper = get_unit_mapper('base_units.yml')
    tables = main(common_dicts, segment_dicts, base_mapper)    
    print_reference(tables)
    

    