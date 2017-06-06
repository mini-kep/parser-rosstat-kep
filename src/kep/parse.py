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
import itertools
import pandas as pd  

import splitter
from cell import filter_value

import cfg
from cfg import spec as SPEC
from cfg import units as UNITS
from cfg import exclude as EXCLUDE

ENC = 'utf-8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')

LABEL_SEP = "__"
SILENT = True

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

# Regex: 
#   (\d{4})    4 digits
#   \d+\)      comment like "1)"
#   (\d+\))*   any number of comments 
#   \s*        any number of whitespaces
YEAR_CATCHER = re.compile('(\d{4})(\d+\))*\s*')

def get_year(string: str, rx=YEAR_CATCHER):
    """Extract year from string *string*. 
       Return None if year is not valid or not in plausible range."""
    match = re.match(rx, string)
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

# hold headres and datarows n table

# [4, 5, 12, 13, 17]
VALID_ROW_LENGTHS = list(splitter.ROW_LENGTH_TO_FUNC_MAPPER.keys())

class Table():    
    def __init__(self, headers, datarows):
        # WONTFIX: naming deadend with three headers ;)
        #    NOTE: header lines accessible via table.header.textrows
        self.header = Header(headers)
        self.datarows = datarows
        self.coln = max([len(d['data']) for d in self.datarows])
        self.validate_coln()
        
    def validate_coln(self, silent = SILENT):             
        if self.coln not in VALID_ROW_LENGTHS:
            for row in self.datarows:
                if len(row) not in VALID_ROW_LENGTHS:
                    if not silent:
                        print("\nWARNING: "
                                "unexpected row length {}".format(self.coln))
                        print(self.header)   
                        print(row['data'])      
                
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
    
    def __flush_datarow_values__(self):
        for row in self.datarows:
            for x in row['data']:
                yield x
    
    @property
    def label(self): 
        vn = self.header.varname
        u = self.header.unit
        if vn and u:
            return vn + LABEL_SEP + u        

    def is_defined(self):
        return self.label and self.splitter_func 
    
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
    UNKNOWN = "-"
    
    def __init__(self, csv_dicts):
        self.varname = None
        self.unit = None      
        self.textlines = [d['head'] for d in csv_dicts]
        # ignore comments
        self.textlines = [x for x in self.textlines if not x.startswith("___")]
        self.processed = odict((line, self.UNKNOWN) for line in self.textlines)
        
    
    def set_varname(self, pdef, units, silent=SILENT):        
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
                        if not silent:
                            print("WARNING: unit not found in  <" + line + ">")
            # something from known_headers must be found only once         
            assert just_one <= 1
                    
    def set_unit(self, units):
        for line in self.textlines:            
            unit = get_unit(line, units)
            if unit:
                self.unit = unit
                # if unit was found at the start of line mark this line as known
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
    """For tables without _varname_ copy _varname_ from previous table.
       Apply to tables that do not have any unknown rows.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.header.varname is None:
           if not table.header.has_unknown_lines():
               table.header.varname = prev_table.header.varname
            
def get_tables(csv_dicts, pdef, units=UNITS):
    tables = [t.parse(pdef, units) for t in split_to_tables(csv_dicts)]
    fix_multitable_units(tables)
    return tables 

def get_all_tables(csv_path, spec=SPEC, units=UNITS):
    csv_dicts = read_csv(csv_path) 
    ds = DictStream(csv_dicts)
    all_tables = []
    # use additional parsing defintions
    for pdef in spec.additional:
        csv_segment = ds.pop(pdef)
        tables = get_tables(csv_segment, pdef, units)
        all_tables.extend(tables)
    # use default parsing defintion
    pdef = spec.main
    csv_segment = ds.remaining_csv_dicts()
    tables = get_tables(csv_segment, pdef, units)
    all_tables.extend(tables)
    return all_tables


def get_all_valid_tables(csv_path, spec=SPEC, units=UNITS, exclude=EXCLUDE):
    all_tables = get_all_tables(csv_path, spec, units)
    return [t for t in all_tables if t.is_defined() and t.label not in exclude]


class RowReader():
    
    def __init__(self, label, splitter_func):
        self.label = label
        self.splitter_func = splitter_func
        
    def parse_row(self, year, values):
        a_value, q_values, m_values = self.splitter_func(values)
        a_dict = None
        q_dicts = []
        m_dicts = []
        
        if a_value:
            a_dict = dict(label=self.label,
                          freq='a',
                          year=year, 
                          value=filter_value(a_value))
        if q_values:
            for t, val in enumerate(q_values):
                if val:
                    d = dict(label=self.label,
                             freq='q',
                             year=year, 
                             value=filter_value(val),
                             qtr=t+1)
                    q_dicts.append(d)
        
        if m_values:
            for t, val in enumerate(m_values):
                if val:
                    d = dict(year=year,
                             label=self.label,
                             freq='m',
                             value=filter_value(val),
                             month=t+1)
                    m_dicts.append(d)        
        return a_dict, q_dicts, m_dicts

class Emitter():
    """Emitter extracts and holds annual, quarterly and monthly values
       for a given table with label and splitter_func."""
        
    def __init__(self, table):
        if not table.label:
            raise ValueError("Table label not defined, cannot create Emitter()"
                             "for " + table.__str__())
        if not table.splitter_func:
            raise ValueError("Table splitter not defined, cannot create Emitter()"
                             "for " + table.__str__())        
        self.a = []
        self.q = []
        self.m = []        
        rr = RowReader(table.label, table.splitter_func)
        for row in table.datarows:            
            if row['data']:
                year = get_year(row['head'])
                a, q, m = rr.parse_row(year, row['data'])
                if a: 
                    self.a.append(a)
                if q:
                    self.q.extend(q)
                if m:
                    self.m.extend(m)
                
    def emit_a(self):
        return self.a
    
    def emit_q(self):    
        return self.q
    
    def emit_m(self):        
        return self.m
    

class Datapoints():
    def __init__(self, tables):
        self.emitters = [Emitter(t) for t in tables if t.is_defined()]
        
    # label can be 'GDP__rog' and 'GDP'   
    def emit_by_method(self, method_name):
        if method_name not in ["emit_a", "emit_q", "emit_m"]:
            raise ValueError(method_name)        
        for e in self.emitters:
            for x in getattr(e, method_name)():                
                    yield x
                        
    def get(self, freq, label, year):
        assert freq in "aqm"
        gen = dict(a=self.emit_a, q=self.emit_q, m=self.emit_m)[freq]()                       
        gen = filter(lambda x: x['label'].startswith(label), gen)
        return filter(lambda x: x['year'] == year, gen)
                        
    def emit_a(self):
        return self.emit_by_method("emit_a")
    
    def emit_q(self):
        return self.emit_by_method("emit_q")

    def emit_m(self):
        return self.emit_by_method("emit_m")
                
    def datapoints(self):
        return itertools.chain(self.emit_a(), self.emit_q(), self.emit_m())                
        
    def is_included(self, datapoint):
        """Return True if *datapoint* is in *self.datapoints*"""        
        return datapoint in list(self.datapoints())

    def unique_varnames(self):
        datapoints = itertools.chain(self.emit_a(), self.emit_q(), self.emit_m())
        return sorted(list(set(p['varname'] for p in datapoints)))

    @functools.lru_cache()
    def unique_varheads(self):
        vh = [x.split(LABEL_SEP)[0] for x in self.unique_varnames()]
        return sorted(list(set(vh)))


# list(x for x in d.emit_a() if x['year'] in (1999, 2014, 2016))
VALID_DATAPOINTS =  [
{'freq': 'a', 'label': 'GDP__bln_rub', 'value': 4823.0, 'year': 1999},
{'freq': 'a', 'label': 'GDP__yoy', 'value': 106.4, 'year': 1999},
        
{'freq': 'a', 'label': 'EXPORT_GOODS_TOTAL__bln_usd', 'value': 75.6, 'year': 1999},
{'freq': 'a', 'label': 'IMPORT_GOODS_TOTAL__bln_usd', 'value': 39.5, 'year': 1999},
        
#{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub', 'value': 26766.1, 'year': 2014},
#{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_FEDERAL__bln_rub', 'value': 14496.9, 'year': 2014},
#{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub', 'value': 8905.7, 'year': 2014},

#{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub', 'value': 30888.8, 'year': 2016},
#{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_FEDERAL__bln_rub', 'value': 14831.6, 'year': 2014},
#{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub', 'value': 9353.3, 'year': 2014},

#{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_FEDERAL__bln_rub', 'value': -334.7, 'year': 2014},
#{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub', 'value': -447.6, 'year': 2014},

{'freq': 'm', 'label': 'EXPORT_GOODS_TOTAL__bln_usd', 'month': 1, 'value': 4.5, 'year': 1999}

]  
 
def approve_csv(year=None, month=None, valid_datapoints=VALID_DATAPOINTS):
    csv_path = cfg.get_path_csv(year,month) 
    print ("File:", csv_path)
    tables = get_all_valid_tables(csv_path)
    dps = Datapoints(tables)
    for x in valid_datapoints:
        if dps.is_included(x):
            pass
        else: 
            msg1 = "Not found in dataset: {}".format(x)
            msg2 = "\nDate: {}, {}".format(year, month)
            msg3 = "\nFile: {}".format(csv_path)
            raise ValueError(msg1+msg2+msg3)
    print("Test values parsed OK.") 
    
    f = Framer(dps) 
    dfa = f.get_dfa()
    dfq = f.get_dfq()
    dfm = f.get_dfm()
    # FIXME - check control values in dataframe
    print("Dataframes created OK.") 
    

def approve_latest():
    approve_csv(year=None, month=None)


def filled_dates(available_dates=cfg.DATES):
    for date in reversed(available_dates): 
        csv_path = cfg.get_path_csv(*date) 
        if csv_path.exists() and csv_path.stat().st_size > 0:
            yield date
    
def approve_all(valid_datapoints=VALID_DATAPOINTS):
    for date in filled_dates():
        approve_csv(*date, valid_datapoints)   

def all_values():
    # emit all values for debugging
    csv_path = cfg.get_path_csv()
    for t in get_all_tables(csv_path):
         for x in t.__flush_datarow_values__():
             yield x

#FIXME: maybe use just one library?
from datetime import datetime
from calendar import monthrange

def get_end_of_monthdate(y, m):
    dm = datetime(year=y, month=m, day=monthrange(y, m)[1])
    return pd.Timestamp(dm) 


def get_end_of_quarterdate(y, q):
    dq = datetime(year=y, month=q*3, day=monthrange(y, q*3)[1])
    return pd.Timestamp(dq)  


class Frame():
    """Accept datapoints and emit pandas dataframeы"""
    
    def __init__(self, datapoints):  
        assert isinstance(datapoints, Datapoints) 
        self._dfa = pd.DataFrame(datapoints.emit_a())
        self._dfq = pd.DataFrame(datapoints.emit_q())
        self._dfm = pd.DataFrame(datapoints.emit_m())
        self.check_for_duplicates()

    def check_for_duplicates(self):
        for df in self._dfa, self._dfq, self._dfm:
            #FIXME: change to raise Exception
            assert df[df.duplicated(keep=False)].empty  
                      
    # TO DISCUSS: get_df*() creates data every time we call them,
    #             may create self.dfa, etc and return.
    
    def get_dfa(self):
        """Returns pandas dataframe with ANNUAL data."""                
        return self._dfa.pivot(columns='label', values='value', index='year')        

    def get_dfq(self):
        """Returns pandas dataframe with QUARTERLY data."""
        dfq = self._dfq
        # add time index
        dfq["time_index"] = dfq.apply(lambda x: get_end_of_quarterdate(x['year'], x['qtr']), axis=1)
        # reshape
        dfq = dfq.pivot(columns='label', values='value', index='time_index')
        # add extra columns
        dfq.insert(0, "year", dfq.index.year)    
        dfq.insert(1, "qtr", dfq.index.quarter)
        return dfq

    def get_dfm(self):
        """Returns pandas dataframe with MONTHLY data."""
        dfm = self._dfm
        # add time index
        dfm["time_index"] = dfm.apply(lambda x: get_end_of_monthdate(x['year'], x['month']), axis=1)
        # reshape
        dfm = dfm.pivot(columns='label', values='value', index='time_index')
        # add extra columns
        dfm.insert(0, "year", dfm.index.year)
        dfm.insert(1, "month", dfm.index.month)
        return dfm     
     
    def save(self, folder_path):                
        self.get_dfa().to_csv(folder_path / 'dfa.csv')
        self.get_dfq().to_csv(folder_path / 'dfq.csv')
        self.get_dfm().to_csv(folder_path / 'dfm.csv')  
        print("Saved dataframes to", folder_path)

#FIXME: use ths functions to catch duplicates early
def duplicates(*items):
    array = list(*items)
    __occurences__ = {x:array.count(x) for x in array} 
    return [k for k,v in __occurences__.items() if v>1]

def dfs(year=None, month=None):
    """Shorthand for obtaining latest dataframes."""
    csv_path = cfg.get_path_csv(year, month)     
    tables = get_all_valid_tables(csv_path)
    dps = Datapoints(tables)
    fr = Frame(dps)    
    dfa = fr.get_dfa()
    dfq = fr.get_dfq()
    dfm = fr.get_dfm()
    return dfa, dfq, dfm

def save_dfs(year=None, month=None):
    #FIXME: maybe rename get_interim_csv_path()
    csv_path = cfg.get_path_csv(year, month)     
    tables = get_all_valid_tables(csv_path)
    dps = Datapoints(tables)
    frame = Frame(dps)
    processed_folder = cfg.get_processed_folder(year, month)
    frame.save(processed_folder)   
    
def save_all_dfs():
    for date in filled_dates():
         save_dfs(*date)   
    


if __name__=="__main__":    
    
    # check for latest date           
    approve_csv()               
    
    # check all dates, runs slow (about 20 sec.) + may fail if dataset not complete      
    # approve_all()
    
    # interim to processed data cycle: (year, month) -> 3 dataframes
    year, month = 2017, 4 #use None, None for latest values
    # source csv file
    csv_path = cfg.get_path_csv(year, month)  
    # break csv to tables with variable names
    tables = get_all_valid_tables(csv_path)
    # emit values from tables
    dps = Datapoints(tables)    
    # convert stream values to pandas dataframes     
    frame = Frame(datapoints=dps)
    # save dataframes to csv files  
    folder = cfg.get_processed_folder(year, month)    
    frame.save(folder)       
    
    # sample access - datapoints
    assert list(dps.get("a", "GDP", 1999)) == [{'freq': 'a', 'label': 'GDP__bln_rub', 'value': 4823.0, 'year': 1999},
                                               {'freq': 'a', 'label': 'GDP__yoy', 'value': 106.4, 'year': 1999}]
    # sample access - dataframes
    dfa = frame.get_dfa()
    dfq = frame.get_dfq()
    dfm = frame.get_dfm()    
    assert dfa.loc[1999,].__str__() == """label
EXPORT_GOODS_TOTAL__bln_usd                  75.6
EXPORT_GOODS_TOTAL__yoy                     101.5
GDP__bln_rub                               4823.0
GDP__yoy                                    106.4
GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub    1258.0
GOV_EXPENSE_ACCUM_FEDERAL__bln_rub          666.9
GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub       653.8
GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub    1213.6
GOV_REVENUE_ACCUM_FEDERAL__bln_rub          615.5
GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub       660.8
GOV_SURPLUS_ACCUM_FEDERAL__bln_rub          -51.4
GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub         7.0
IMPORT_GOODS_TOTAL__bln_usd                  39.5
IMPORT_GOODS_TOTAL__yoy                      68.1
IND_PROD__yoy                                 NaN
Name: 1999, dtype: float64"""

    assert dfm.loc["2017-01",].transpose().__str__() == """time_index                               2017-01-31
label                                              
year                                         2017.0
month                                           1.0
EXPORT_GOODS_TOTAL__bln_usd                    25.1
EXPORT_GOODS_TOTAL__rog                        80.3
EXPORT_GOODS_TOTAL__yoy                       146.6
GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub      1682.9
GOV_EXPENSE_ACCUM_FEDERAL__bln_rub           1230.5
GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub         452.2
GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub      1978.8
GOV_REVENUE_ACCUM_FEDERAL__bln_rub           1266.0
GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub         493.7
GOV_SURPLUS_ACCUM_FEDERAL__bln_rub             35.5
GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub          41.5
IMPORT_GOODS_TOTAL__bln_usd                    13.7
IMPORT_GOODS_TOTAL__rog                        70.2
IMPORT_GOODS_TOTAL__yoy                       138.8
IND_PROD__rog                                  76.2
IND_PROD__yoy                                 102.3
IND_PROD__ytd                                 102.3"""
    
    
    # TEST:
    # all varnames from definition are read from csv file
    
    # CRITICAL PATH:    
    # analysis: check revisions of key series by date
    #          -> use different folder for this analysis code
    # Russian economy by this model
    
    # TODO-PARSING:         
    # save processed files for differents dates = save_all_dfs()
    # convert more existing parsing definitions to cfg.py    
    # add more control datapoints    
    
    # TODO-FRONTEND:
    # var descriptions in cfg.py
    # generate frontend with sparlines           
    
    # NOT CRITICAL:
    # merge code from cell.py
    # finilise Table-Emitter-Dataset dicsussion 
    # diff GOV_EXPENSE_ACCUM, GOV_REVENUE_ACCUM
    
    # FOR REVIEW:
    # write csv files to 'processed' via to_csv()    
    # shuttiing warnings with SILENT flag    
    # pandas interface for Datapoints   
