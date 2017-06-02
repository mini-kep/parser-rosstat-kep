"""Parse tables from raw CSV file using parsing defintion.

   Parsring defintion contains:
   -  parsing boundaries - start and end lines of CSV file segment
   -  link between table headers ("Объем ВВП") and variable names ("GDP")
   -  units of measurement dictionary ("мдрд.руб." -> "bln_rub")

   Parsing procedure:
   - cut out a segment of csv file as delimited by start and end lines (1)
   - save remaining parts of csv file for further parsing      
   - break csv segment into tables, each table containing headers and data rows
   - parse table headers to obtain variable name ("GDP") and unit ("bln_rub")             
   - for tables with varname and unit: 
        split datarows to obtain annual, quarter and monthly values
        emit values as frequency-label-date-value dicts
"""

import csv
import re
from enum import Enum, unique
import functools
from collections import OrderedDict as odict  

import splitter
from cell import filter_value

from cfg import spec
from cfg import units
from cfg import exclude

ENC = 'utf-8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')

LABEL_SEP = "__"


# csv file access
def to_csv(rows, path):
    """Accept iterable of rows *rows* and write in to *csv_path*"""
    with path.open('w', encoding=ENC) as csvfile:
        filewriter = csv.writer(csvfile, **CSV_FORMAT)
        for row in rows:
            filewriter.writerow(row)
    return path

def from_csv(path):
    """Get iterable of rows from *csv_path*"""
    with path.open(encoding=ENC) as csvfile:
       csvreader = csv.reader(csvfile, **CSV_FORMAT)
       for row in csvreader:
             yield row  
         
def to_dict(row):
    """Make dictionary based on non-empty *row*"""
    if row and row[0]:
       return dict(head=row[0], data=row[1:])
    else:
       return None
    
def read_csv(path):
    """Yield non-empty dictionaries with 'head' and 'data' keys from *path*"""
    raw = from_csv(path)
    csv_dicts = map(to_dict, raw)    
    return filter(lambda x: x is not None, csv_dicts) 


# DictStream() - holder for csv rows
def is_matched(pat, textline):
    # kill " in both strings
    pat = pat.replace('"','') 
    textline = textline.replace('"','')
    if pat:
        return textline.startswith(pat)
    else:
        return False 

class DictStream():    
    def __init__(self, csv_dicts):
        # consume *csv_dicts*, maybe it is a generator
        self.csv_dicts = [x for x in csv_dicts]
    
    def is_found(self, pat):
        for csv_dict in self.csv_dicts:
            if is_matched(pat, csv_dict['head']):
                return True
        return False
          
    def remaining_csv_dicts(self):
        return self.csv_dicts

    def pop(self, pdef):
        # walk by different versions of start/end lines eg 1.10... or 1.9...
        for marker in pdef.markers:
            s = marker['start'] 
            e = marker['end'] 
            if self.is_found(s) and self.is_found(e):
                return self.pop_segment(s, e)
        self.echo_error_ends_not_found(pdef)
        return []    
        
    def echo_error_ends_not_found(self, pdef):
        print("ERROR: start or end line not found in *csv_dicts*")              
        for marker in pdef.markers:
            s = marker['start'] 
            e = marker['end'] 
            print("   ", self.is_found(s), "<{}>".format(s))
            print("   ", self.is_found(e), "<{}>".format(e))                       
    
    def pop_segment(self, start, end):
        """Pops elements of self.csv_dicts between [start, end). 
           Recognises element occurences by index *i*.
           Modifies *self.csv_dicts*."""           
        we_are_in_segment = False
        segment = []
        i = 0
        while i < len(self.csv_dicts):
            row = self.csv_dicts[i]
            line = row['head']
            if is_matched(start, line):
                we_are_in_segment = True
            if is_matched(end, line):
                break
            if we_are_in_segment:
                segment.append(row)
                del self.csv_dicts[i]
            else:    
                # else is very important, wrong indexing without it
                i += 1
        return segment


# break csv segment into tables
def get_year(string: str):
    """Extract year from string *string*. 
       Return None if year is not valid or not in plausible range."""
    # Regex: 
    #   (\d{4})    4 digits
    #   \d+\)      comment like "1)"
    #   (\d+\))*   any number of comments 
    #   \s*        any number of whitespaces
    match = re.match(r'(\d{4})(\d+\))*\s*', string)
    if match:
        year = int(match.group(1))
        if year >= 1991:
            return year
    return None

def is_year(s: str) -> bool:
    return get_year(s) is not None


def is_data_row(row):
    return is_year(row['head'])


@unique
class RowType(Enum):
    UNKNOWN = 0
    DATA = 1
    SECTION = 2
    HEADER = 3

@unique
class State(Enum):
    INIT = 1
    DATA = 2
    UNKNOWN = 3    
    
def split_to_tables(csv_dicts):
    datarows = []
    headers = []
    state = State.INIT
    for d in csv_dicts:        
        if is_data_row(d):
            datarows.append(d)
            state = State.DATA
        else:
            if state == State.DATA: # table ended
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(d)
            state = State.UNKNOWN
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)

# hold and process info in table

class DataRows():
    
    def __init__(self, label, splitter_func):
        self.label = label
        self.splitter_func = splitter_func
        
    def parse_row(self, year, values):
        a, qs, ms = self.splitter_func(values)
        
        self.a = []
        if a:
            self.a = dict(label=self.label,
                           freq='a',
                           year=year, 
                           value=filter_value(a))
        self.q = []
        if qs:
            for t, val in enumerate(qs):
                if val:
                    if val == "-": import pdb; pdb.set_trace()
                    self.q.append(dict(label=self.label,
                                       freq='q',
                                       year=year, 
                                       value=filter_value(val),
                                       qtr=t+1))
        self.m = []        
        if ms:
            for t, val in enumerate(ms):
                if val:
                    if val == "-": import pdb; pdb.set_trace()
                    self.m.append(dict(year=year,
                                       label=self.label,
                                       freq='m',
                                       value=filter_value(val),
                                       month=t+1))        
    

class Table():    
    def __init__(self, headers, datarows):
        self.headers = headers
        self.header = Header(headers)
        self.datarows = datarows
        self.coln = max([len(d['data']) for d in self.datarows])          
                
    def parse(self, pdef, units):        
        self.header.set_varname(pdef, units)       
        self.header.set_unit(units)
        self.set_splitter(pdef)
        return self           
    
    def set_splitter(self, pdef):
        funcname = pdef.reader
        if funcname:
            self.splitter_func = splitter.get_custom_splitter(funcname)
        else:
            self.splitter_func = splitter.get_splitter(self.coln) 
    
    def calc(self):         
        self.a = []
        self.q = []
        self.m = []        
        ds = DataRows(self.label, self.splitter_func)
        for row in self.datarows:            
            if row['data']:
                year = get_year(row['head'])
                ds.parse_row(year, row['data'])
                self.a.append(ds.a)
                self.q.extend(ds.q)
                self.m.extend(ds.m)
        return self
                
    def emit(self, freq):
        assert freq in 'aqm'
        try:        
            values = {'a':self.a, 'q':self.q, 'm':self.m}[freq]
        except:
            import pdb; pdb.set_trace()
        return iter(values)

    @property
    def label(self): 
        if self.header:
            vn = self.header.varname
            u = self.header.unit
            if vn and u:
                return vn + LABEL_SEP + u        

    @property    
    def nrows(self):
        return len(self.datarows)
    
    @property
    def npoints(self):
        try:
            return len(self.a) + len(self.q) + len(self.m)
        except:
            return 0
        
    def __str__(self):
        msg = "\nTable with {} header(s) and {} datarow(s)".format(len(self.textrows),
                                                                 self.nrows)
        if self.header:
              msg += "\n"+self.header.__str__() 
        if self.label:                               
              msg += "\nlabel: {}".format(self.label) 
        return msg 
        
    def __repr__(self):
        return "{} ({}/{})".format(self.label, 
                                   self.npoints,
                                   self.nrows)     

# hold and process info in table header
class Header():
    
    KNOWN = "+"
    UNKNOWN = "+"
    
    def __init__(self, csv_dicts):
        self.varname = None
        self.unit = None      
        self.textlines = [d['head'] for d in csv_dicts]
        self.processed = odict((line, self.UNKNOWN) for line in self.textlines)
        
    
    def set_varname(self, pdef, units):        
        varname_dict = pdef.headers
        known_headers = varname_dict.keys()
        for line in self.textlines:
            for header in known_headers:
                just_one = 0 
                if header in line:
                    just_one += 1
                    self.processed[line] = self.KNOWN
                    self.varname = varname_dict[header]
                    self.unit = get_unit(line, units)
                    if self.unit is None:
                        print("Unit not found in: " + line)
            # known_headers must be found only once         
            assert just_one <= 1
                    
    def set_unit(self, units):
        for line in self.textlines:            
            unit = get_unit(line, units)
            if unit:
                self.unit = unit
                # if unit was found at the start of line, delete this line 
                for u in units.keys():
                   if line.startswith(u):
                      self.processed[line] = "+"                
    
    def has_unknown_lines(self):
        return self.UNKNOWN in self.processed.values()
    
    def __str__(self):
        show = [v+" <"+k+">" for k,v in self.processed.items()] 
        return ("\n".join(show) +
                "\nvarname: {}, unit: {}".format(self.varname, self.unit))
               
def get_unit(line, units):
    for k in units.keys():
        if k in line:  
            return units[k]
    return None

def fix_multitable_units(tables):
    """For tables which do not have parameter definition,
       but do not have any unknown rows, copy parameter 
       from previous table.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.header.varname is None:
           if not table.header.has_unknown_lines():
               table.header.varname = prev_table.header.varname
            
def get_tables(csv_dicts, pdef, units):
    tables = [t.parse(pdef, units) for t in split_to_tables(csv_dicts)]
    fix_multitable_units(tables)
    # FIXME: move around or delete commment strings starting with "___"
    return [t for t in tables if t.label and t.label not in exclude]


def get_all_tables(csv_path, spec):
    csv_dicts = read_csv(csv_path) 
    ds = DictStream(csv_dicts)
    all_tables = []
    # use additional parsing defintions
    # FIXME: spec order not guaranteed
    for pdef in spec[1:]:
        csv_segment = ds.pop(pdef)
        tables = get_tables(csv_segment, pdef, units)
        all_tables.extend(tables) 
    # use default parsing defintion
    # FIXME: spec order not guaranteed
    pdef = spec[0]
    csv_segment = ds.remaining_csv_dicts()
    tables = get_tables(csv_segment, pdef, units)
    all_tables.extend(tables)
    return all_tables

class Datapoints():
    def __init__(self, tables):
        self.tables = tables
        self.datapoints = list(self.walk_by_blocks())

    def walk_by_blocks(self):
        for t in self.tables:
            t.calc()
            for freq in "aqm":
                 for x in t.emit(freq):
                     if x:
                         yield x

    def emit(self, freq):
        if freq not in 'aqm':
            raise ValueError(freq)            
        for p in self.datapoints:
            if p['freq'] == freq and p['value']:
                yield p

    def is_included(self, datapoint):
        """Return True if *datapoint* is in *self.datapoints*"""
        return datapoint in self.datapoints

    def unique_varnames(self):
        varnames = []
        for freq in 'aqm':
            varnames.extend([p['varname'] for p in self.emit(freq)])
        return sorted(list(set(varnames)))

    @functools.lru_cache()
    def unique_varheads(self):
        vh = [x.split(LABEL_SEP)[0] for x in self.unique_varnames()]
        return sorted(list(set(vh)))

if __name__=="__main__": 
    assert get_year("19991)") == 1999
    
    
    from cfg import get_path_csv    
    csv_path = get_path_csv() 

    tables = get_all_tables(csv_path, spec)
    d = Datapoints(tables)
    a = list(x for x in d.emit('a') if x['year'] in (1999, 2014, 2016))
    
    #FIXME add more datapoints
    valid_datapoints =  [
{'freq': 'a', 'label': 'GDP__bln_rub', 'value': 4823.0, 'year': 1999},
{'freq': 'a', 'label': 'GDP__rog', 'value': 106.4, 'year': 1999},
        
{'freq': 'a', 'label': 'EXPORT_GOODS_TOTAL__bln_usd', 'value': 75.6, 'year': 1999},
{'freq': 'a', 'label': 'IMPORT_GOODS_TOTAL__bln_usd', 'value': 39.5, 'year': 1999},
        
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub', 'value': 26766.1, 'year': 2014},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_FEDERAL__bln_rub', 'value': 14496.9, 'year': 2014},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub', 'value': 8905.7, 'year': 2014},

{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub', 'value': 30888.8, 'year': 2016},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_FEDERAL__bln_rub', 'value': 14831.6, 'year': 2014},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub', 'value': 9353.3, 'year': 2014},

{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_FEDERAL__bln_rub', 'value': -334.7, 'year': 2014},
{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub', 'value': -447.6, 'year': 2014}
]        

    for x in valid_datapoints:
        assert x in a 
