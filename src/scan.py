from copy import copy
from profilehooks import profile

from csv2df import read_tables, unpack_dataframes, validate, ParsingParameters
from dates import date_span
from locations import interim_csv

ALL_DATES = date_span('2009-04', '2018-06')       


def iterate(x)-> list:
    """Mask string as [x] list."""
    if isinstance(x, str):
        return [x]
    else:
        return x

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

def get_tables(year, month):
    path = interim_csv(year, month)
    return read_tables(path)

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

@profile(immediate=True, entries=20)
def main(common_dicts, segment_dicts, base_mapper):
    """Run parsing for all dates and return latest set of tables."""
    for year, month in ALL_DATES:
        print(year, month)
        tables = get_tables(year, month)
        last = get_parsed_tables(tables, common_dicts, segment_dicts,  base_mapper)
    return last    

if __name__ == '__main__':
    # must lazy import, will loop otherwise
    from man import print_reference
    p = ParsingParameters()
    tables = main(p.common_dicts, p.segment_dicts, p.mapper)  
    values = datapoints(tables)    
    print_reference(tables, p.grouper)
    validate(values, p.mandatory, p.optional)    
    