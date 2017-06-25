"""Parse raw CSV file using parsing specification.

Main call:

   Vintage(year, month).save()

"""

from enum import Enum, unique
from collections import OrderedDict as odict
import csv
import itertools
import re
import warnings

from datetime import date
import calendar 

import pandas as pd

import splitter
import files
from cfg import spec as SPEC
from cfg import units as UNITS

# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)

ENC = 'utf-8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')


# label handling
def make_label(vn, unit, sep="_"):
    return vn + sep + unit


def split_label(label):
    return extract_varname(label), extract_unit(label)


def extract_varname(label):
    words = label.split('_')
    return '_'.join(itertools.takewhile(lambda word: word.isupper(), words))


def extract_unit(label):
    words = label.split('_')
    return '_'.join(itertools.dropwhile(lambda word: word.isupper(), words))


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


def read_csv(path):
    """Yield non-empty dictionaries with 'head' and 'data' keys from *path*"""
    raw_csv_rows = from_csv(path)
    filled_csv_rows = filter(lambda row: row and row[0], raw_csv_rows)
    return map(Row, filled_csv_rows)


class Tables:
    """Returns tables from *csv_path* by .get_all() method."""

    def __init__(self, csv_path):
        rows = read_csv(csv_path)
        self.row_stack = RowStack(rows)

    def get_all(self, spec=SPEC, units=UNITS):
        all_tables = []
        # use additional parsing definitions first
        for pdef in spec.additional:
            csv_segment = self.row_stack.pop(pdef)
            tables = get_tables_from_rows_segment(csv_segment, pdef, units)
            all_tables.extend(tables)
        # use default parsing definition on remaining rows
        pdef = spec.main
        csv_segment = self.row_stack.remaining_rows()
        tables = get_tables_from_rows_segment(csv_segment, pdef, units)
        all_tables.extend(tables)
        return all_tables

    def get_defined(self):
        return [t for t in self.get_all() if t.is_defined()]


YEAR_CATCHER = re.compile('(\d{4}).*')


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from string *string*.
       Returns None if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991:
            return year
    return None


def is_year(string: str) -> bool:
    return get_year(string) is not None


class Row:
    """Single CSV row representation."""

    def __init__(self, row):
        self.name = row[0]
        self.data = row[1:]        

    def len(self):
        return len(self.data)

    def is_datarow(self):
        return is_year(self.name)

    def __str__(self):
        return "{} | {}".format(self.name, ' '.join(self.data))

    def __repr__(self):
        return self.__str__()


class RowStack:
    """Holder for CSV rows."""

    def __init__(self, rows):
        # consume *rows*, maybe it is a generator
        self.rows = [r for r in rows]

    @staticmethod
    def is_matched(pat, textline):
        """Returns True if *textline* starts with *pat*, False otherwise
           Ignores "
        """
        pat = pat.replace('"', '')
        if pat:
            textline = textline.replace('"', '')
            return textline.startswith(pat)
        else:
            return False

    def is_found(self, text):
        for row in self.rows:
            if self.is_matched(text, row.name):
                return True
        return False

    def remaining_rows(self):
        return self.rows

    def pop(self, pdef):
        # walks by different versions of start/end lines eg 1.10... or 1.9...
        for marker in pdef.markers:
            s = marker['start']
            e = marker['end']
            if self.is_found(s) and self.is_found(e):
                return self.pop_segment(s, e)
        self.echo_error_ends_not_found(pdef)
        return []

    def echo_error_ends_not_found(self, pdef):
        print("ERROR: start or end line not found in *self.rows*")
        for marker in pdef.markers:
            s = marker['start']
            e = marker['end']
            print("   ", self.is_found(s), "<{}>".format(s))
            print("   ", self.is_found(e), "<{}>".format(e))

    def pop_segment(self, start, end):
        """Pops elements of self.row between [start, end).
           Recognises element occurrences by index *i*.
           Modifies *self.rows*."""
        we_are_in_segment = False
        segment = []
        i = 0
        while i < len(self.rows):
            row = self.rows[i]
            line = row.name
            if self.is_matched(start, line):
                we_are_in_segment = True
            if self.is_matched(end, line):
                break
            if we_are_in_segment:
                segment.append(row)
                del self.rows[i]
            else:
                # else is very important, wrong indexing without it
                i += 1
        return segment


# classes for split_to_tables()
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


def split_to_tables(rows):
    """Yields Table() instances from *rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        if row.is_datarow():
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:  # table ended
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.UNKNOWN
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class Table:
    """Headers and datarows."""

    # [4, 5, 12, 13, 17]
    VALID_ROW_LENGTHS = list(splitter.ROW_LENGTH_TO_FUNC_MAPPER.keys())

    def __init__(self, headers, datarows):
        # WONTFIX: naming deadend with three headers in one line
        self.header = Header(headers)
        self.datarows = datarows
        self.coln = max(row.len() for row in self.datarows)

    def parse(self, pdef, units):
        self.header.set_varname(pdef, units)
        self.header.set_unit(units)
        self.set_splitter(pdef)
        return self

    def set_splitter(self, pdef):
        funcname = pdef.reader
        if funcname:
            # reader func from pdef overrides other specs
            self.splitter_func = splitter.get_custom_splitter(funcname)
        elif self.coln in self.VALID_ROW_LENGTHS:
            # use standard splitters for standard number of columns
            self.splitter_func = splitter.get_splitter(self.coln)
        else:
            # Trying to parse a table without <year> <values> structure.
            # Such tables are currently out of scope of parsing definition.
            warnings.warn("Unexpected row length {}\n{}".format(self.coln, self))

    @property
    def label(self):
        vn = self.header.varname
        u = self.header.unit
        if vn and u:
            return make_label(vn, u)

    def is_defined(self):
        return self.label and self.splitter_func

    def echo_error_table_not_valid(self):
        if not self.label:
            raise ValueError("Label not defined for:\n{}".format(self))
        if not self.splitter_func:
            raise ValueError("Splitter func not defined for:\n{}".format(self))

    def __str__(self):
        text = [row.__str__() for row in self.datarows]
        horizontal_break = "-" * max(len(t) for t in text)
        return "\n".join(["Table for variable {}".format(self.label),
                          "Number of columns: {}".format(self.coln),
                          self.header.__str__(),
                          horizontal_break,
                          '\n'.join(text),
                          horizontal_break])

    def __repr__(self):
        return "Table {} ".format(self.label) + \
               "({} headers,".format(len(self.header.textlines)) + \
               " {} datarows)".format(len(self.datarows))


class Header:
    """Table header. Can extract variable label."""

    KNOWN = "+"
    UNKNOWN = "-"

    def __init__(self, rows):
        self.varname = None
        self.unit = None
        self.textlines = [row.name for row in rows
                          if not row.name.startswith("___")]
        self.processed = odict((line, self.UNKNOWN) for line in self.textlines)

    def set_varname(self, pdef, units):
        varname_dict = pdef.headers
        known_headers = varname_dict.keys()
        for line in self.textlines:
            just_one = 0
            for header in known_headers:
                if re.search(r"\b" + header, line) is not None:
                    just_one += 1
                    self.processed[line] = self.KNOWN
                    self.varname = varname_dict[header]
                    unit = self.get_unit(line, units)
                    if unit:
                        self.unit = unit
                    else:
                        # Trying to extract unit of measurement from a header without it.
                        # Usually a proper unit is found in next few header textlines.
                        warnings.warn("unit not found in  <{}>".format(line))
            # anything from known_headers must be found only once
            assert just_one <= 1

    @staticmethod
    def get_unit(line, units):
        for k in units.keys():
            if k in line:
                return units[k]
        return None

    def set_unit(self, units):
        for line in self.textlines:
            unit = self.get_unit(line, units)
            if unit:
                self.unit = unit
                # if unit was found at the start of line, mark line as known
                for u in units.keys():
                    if line.startswith(u):
                        self.processed[line] = self.KNOWN

    def has_unknown_lines(self):
        return self.UNKNOWN in self.processed.values()

    def __str__(self):
        show = ["varname: {}, unit: {}".format(self.varname, self.unit)] + \
               ["{} <{}>".format(v, k) for k, v in self.processed.items()]
        return "\n".join(show)


def fix_multitable_units(tables):
    """For tables without *header.varname* copy *header.varname* from previous table.
       Applies to tables that do not have any unknown rows.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.header.varname is None:
            if not table.header.has_unknown_lines():
                table.header.varname = prev_table.header.varname


def check_required_labels(tables, pdef):
    labels_required = [make_label(varname, unit) for varname, unit in pdef.required]
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in labels_required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels:" + labels_missed.__str__())


def get_tables_from_rows_segment(rows_segment, pdef, units=UNITS):
    tables = [t.parse(pdef, units) for t in split_to_tables(rows_segment)]
    fix_multitable_units(tables)
    check_required_labels(tables, pdef)
    return tables


COMMENT_CATCHER = re.compile("\D*(\d+[.,]?\d*)\s*(?=\d\))")


def to_float(text, i=0):
    i += 1
    if i > 5:
        raise ValueError("Max recursion depth exceeded on '{}'".format(text))
    if not text:
        return False
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        # note: order of checks important
        if " " in text.strip():  # get first value '542,0 5881)'
            return to_float(text.strip().split(" ")[0], i)
        if ")" in text:  # catch '542,01)'
            match_result = COMMENT_CATCHER.match(text)
            if match_result:
                text = match_result.group(0)
                return to_float(text, i)
        if text.endswith(".") or text.endswith(","):  # catch 97.1,
            return to_float(text[:-1], i)
        return False


class DictMaker:
    def __init__(self, year, label):
        self.basedict = {'year': year, 'label':label}

    def a_dict(self, val):
        return {**self.basedict, 'freq': 'a', 'value': to_float(val)}

    def q_dict(self, val, q):
        return {**self.basedict, 'freq': 'q', 'value': to_float(val), 'qtr': q}

    def m_dict(self, val, m):
        return {**self.basedict, 'freq': 'm', 'value': to_float(val),
                'month': m}
        
    def __str__(self):
        return self.basedict.__str__()   
        


class Emitter:
    """Emitter extracts and holds annual, quarterly and monthly values
       for a given Table.

       Table must have defined *label* and *splitter_func*."""

    def __init__(self, table):
        if not table.label or not table.splitter_func:
            table.echo_error_table_not_valid()
        self.a = []
        self.q = []
        self.m = []
        for row in table.datarows:
            dmaker = DictMaker(get_year(row.name), table.label)
            a_value, q_values, m_values = table.splitter_func(row.data)
            if a_value:                
                self.a.append(dmaker.a_dict(a_value))
            if q_values:
                self.q.extend([dmaker.q_dict(val, t+1) 
                               for t, val in enumerate(q_values) if val])                
            if m_values:
                self.m.extend([dmaker.m_dict(val, t+1) 
                               for t, val in enumerate(m_values) if val])

    def emit_a(self):
        return self.a

    def emit_q(self):
        return self.q

    def emit_m(self):
        return self.m


class Datapoints:
    """Produces datapoints using emitters"""

    def __init__(self, tables):
        self.emitters = [Emitter(t) for t in tables if t.is_defined()]
        self.datapoints = list(self.get_datapoints())

    def emit_by_method(self, method_name: str):
        if method_name not in ["emit_a", "emit_q", "emit_m"]:
            raise ValueError("Method name not valid: {}".format(method_name))
        for e in self.emitters:
            emitter_func = getattr(e, method_name)
            for x in emitter_func():
                yield x

    def emit_a(self):
        return self.emit_by_method("emit_a")

    def emit_q(self):
        return self.emit_by_method("emit_q")

    def emit_m(self):
        return self.emit_by_method("emit_m")

    def get(self, freq, label, year):
        assert freq in "aqm"
        emitters_dict = dict(a=self.emit_a, q=self.emit_q, m=self.emit_m)
        gen = emitters_dict[freq]()
        gen = filter(lambda x: x['label'].startswith(label), gen)
        return filter(lambda x: x['year'] == year, gen)

    def get_datapoints(self):
        return itertools.chain(self.emit_a(), self.emit_q(), self.emit_m())

    def is_included(self, datapoint):
        """Returns True if *datapoint* is in *self.datapoints*, False otherwise"""
        return datapoint in self.datapoints


# dataframe dates handling
def month_end_day(year, month):
    return calendar.monthrange(year, month)[1]

def get_date_month_end(year, month):
    day = month_end_day(year, month)
    return pd.Timestamp(date(year, month, day))

def get_date_quarter_end(year, qtr):
    # quarter number should be based at 1
    assert qtr <=4 and qtr >=1  
    month = qtr * 3
    return get_date_month_end(year, month)

def get_date_year_end(year):
    return pd.Timestamp(date(year, 12, 31))

class Frames:
    """Accepts Datapoints() instance and emits pandas DataFrames."""

    def __init__(self, datapoints):
        assert isinstance(datapoints, Datapoints)
        dfa = pd.DataFrame(datapoints.emit_a())
        dfq = pd.DataFrame(datapoints.emit_q())
        dfm = pd.DataFrame(datapoints.emit_m())
        for df in dfa, dfq, dfm:
            # df must have no duplicate rows
            dups = df[df.duplicated(keep=False)]
            if not dups.empty:
                import pdb; pdb.set_trace()
        self.dfa = self.reshape_a(dfa)
        self.dfq = self.reshape_q(dfq)
        self.dfm = self.reshape_m(dfm)

    @staticmethod
    def reshape_a(dfa):
        """Returns pandas dataframe with ANNUAL data."""
        dfa["time_index"] = dfa.apply(lambda x: get_date_year_end(x['year']), axis=1)
        dfa = dfa.pivot(columns='label', values='value', index='time_index')
        dfa.insert(0, "year", dfa.index.year)
        return dfa

    @staticmethod
    def reshape_q(dfq):
        """Returns pandas dataframe with QUARTERLY data."""
        dfq["time_index"] = dfq.apply(lambda x: get_date_quarter_end(x['year'], x['qtr']), axis=1)
        dfq = dfq.pivot(columns='label', values='value', index='time_index')
        dfq.insert(0, "year", dfq.index.year)
        dfq.insert(1, "qtr", dfq.index.quarter)
        return dfq

    @staticmethod
    def reshape_m(dfm):
        """Returns pandas dataframe with MONTHLY data."""
        dfm["time_index"] = dfm.apply(lambda x: get_date_month_end(x['year'], x['month']), axis=1)
        dfm = dfm.pivot(columns='label', values='value', index='time_index')
        dfm.insert(0, "year", dfm.index.year)
        dfm.insert(1, "month", dfm.index.month)
        return dfm

    def save(self, folder_path):
        self.dfa.to_csv(folder_path / 'dfa.csv')
        self.dfq.to_csv(folder_path / 'dfq.csv')
        self.dfm.to_csv(folder_path / 'dfm.csv')
        print("Saved dataframes to", folder_path)
        

VALID_DATAPOINTS = [
            {'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
            {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999},
            {'freq': 'a', 'label': 'EXPORT_GOODS_TOTAL_bln_usd', 'value': 75.6, 'year': 1999},
            {'freq': 'q', 'label': 'IMPORT_GOODS_TOTAL_bln_usd', 'qtr': 1, 'value': 9.1, 'year': 1999},
            {'freq': 'm', 'label': 'RETAIL_SALES_NONFOODS_rog', 'month': 12, 'value': 114.9, 'year': 1999}
        ]


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year, month):
        self.year, self.month = files.filter_date(year, month)
        # get csv source
        self.csv_path = files.get_path_csv(year, month)
        # break csv to tables with variable names
        self.tables = Tables(self.csv_path).get_defined()
        # emit values from tables
        self.dpoints = Datapoints(self.tables)
        # convert stream values to pandas dataframes
        self.frames = Frames(datapoints=self.dpoints)

    def save(self):
        """Save dataframes to CSVs."""
        processed_folder = files.get_processed_folder(self.year, self.month)
        self.frames.save(processed_folder)

    def dfs(self):
        """Shorthand for obtaining dataframes."""
        return self.frames.dfa,  self.frames.dfq,  self.frames.dfm

    def __str__(self):
        return "{} {}".format(self.year, self.month)

    def __repr__(self):
        return "{0!s}({1!r}, {2!r})".format(self.__class__, self.year, self.month)

    def validate(self, valid_datapoints=VALID_DATAPOINTS):
        for x in valid_datapoints:
            if not self.dpoints.is_included(x):
                raise ValueError("Not found in dataset: {}".format(x) +
                                 "File: {}".format(self.csv_path))
        print("Test values parsed OK for", self)


class Collection:
    # Methods to manipulate entire set of data releases

    @staticmethod
    def save_all_dataframes_to_csv():
        for (year, month) in files.filled_dates():
            Vintage(year, month).save()

    @staticmethod
    def approve_latest():
        """Quick check for algorithm on latest available data."""
        vintage = Vintage(year=None, month=None)
        vintage.validate()

    @staticmethod
    def approve_all():
        """Checks all dates, runs slow (about 20 sec.)
           May fail if dataset not complete.
        """
        for (year, month) in files.filled_dates():
            vintage = Vintage(year, month)
            vintage.validate()

# FIXME: review __str__, and __repr__?

if __name__ == "__main__":
    #Collection.approve_latest()
    Collection.approve_all()
    Collection.save_all_dataframes_to_csv()

    year, month = 2017, 4
    vintage = Vintage(year, month)
    dfa, _, dfm = vintage.dfs()

    """
    Parsing definition contains:
   -  parsing boundaries - start and end lines of CSV file segment
   -  link between table headers ("Объем ВВП") and variable names ("GDP")
   -  units of measurement dictionary ("мдрд.руб." -> "bln_rub")

   Parsing procedure:
   - cut out a segment of csv file as delimited by start and end lines
   - save remaining parts of csv file for further parsing
   - break csv segment into tables, each table containing headers and data rows
   - parse table headers to obtain variable name ("GDP") and unit ("bln_rub")
   - for tables with varname and unit:
        split datarows to obtain annual, quarter and monthly values
        emit values as frequency-label-date-value dicts
    """
