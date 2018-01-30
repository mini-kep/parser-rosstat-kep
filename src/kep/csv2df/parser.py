"""Parse [(csv_segment, pdef)... ] inputs into Table() instances using
   parsing specification.

Main call:
   tables = get_tables(rows, SPEC)

"""

from enum import Enum, unique
from collections import OrderedDict as odict

import kep.csv2df.util_row_splitter as splitter
from kep.csv2df.util_label import make_label


__all__ = ['extract_tables']


def extract_tables(csv_segment, pdef):
    """Extract tables from *csv_segment* list Rows instances using
       *pdef* parsing defintion.
    """
    tables = split_to_tables(csv_segment)
    tables = parse_tables(tables, pdef)
    verify_tables(tables, pdef)
    return [t for t in tables if t.label in pdef.required]


def parse_tables(tables, pdef):
    # assign reader function    
    tables = [t.set_splitter(pdef.reader) for t in tables]    
    # parse tables to obtain labels - set label and splitter
    tables = [t.set_label(pdef.mapper, pdef.units) for t in tables]    
    # assign trailing units
    def fix_multitable_units(tables):
        """For tables without *varname* - copy *varname* from previous table.
           Applies to tables where all rows are known rows.
        """
        for prev_table, table in zip(tables, tables[1:]):
            if table.varname is None and not table.has_unknown_lines():
                table.varname = prev_table.varname
    fix_multitable_units(tables)
    return tables


def verify_tables(tables, pdef):
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in pdef.required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels: {}".format(labels_missed))


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
    """Representation of CSV table, has headers and datarows."""

#    # [4, 5, 12, 13, 17]
#    VALID_ROW_LENGTHS = list(splitter.FUNC_MAPPER.keys())
    KNOWN = "+"
    UNKNOWN = "-"    

    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows

        self.lines = odict((row.name, self.UNKNOWN) for row in headers)
        self.coln = max(len(row) for row in self.datarows)
        self.splitter_func = None
       
        self.varname = None
        self.unit = None
        self.datapoints = []

    def set_label(self, varnames_dict, units_dict):
        for row in self.headers:
            varname = row.get_varname(varnames_dict)
            if varname:
                self.varname = varname
                self.lines[row.name] = self.KNOWN
            unit = row.get_unit(units_dict)
            if unit:
                self.unit = unit
                self.lines[row.name] = self.KNOWN
        return self

    def set_splitter(self, reader):
        self.splitter_func = splitter.get_splitter(reader or self.coln)
        return self

    @property
    def label(self):
        vn = self.varname
        u = self.unit
        if vn and u:
            return make_label(vn, u)
        else:
            return None

    def is_defined(self):
        return bool(self.label and self.splitter_func)

    def has_unknown_lines(self):
        return self.UNKNOWN in self.lines.values()

    def __eq__(self, x):
        return self.headers == x.headers and self.datarows == x.datarows

    def __str__(self):
        show = ["Table {} ({} columns)".format(self.label, self.coln),
                '\n'.join(["{} <{}>".format(v, k) for k, v in self.lines.items()]),
                '\n'.join([str(row) for row in self.datarows])
                ]
        return "\n".join(show)

    def __repr__(self):
        return "Table(\n    headers={},\n    datarows={})" \
               .format(repr(self.headers), repr(self.datarows))
               
    def make_datapoint(self, value: str, time_stamp, freq):
        return dict(label=self.label, 
                    value=to_float(value), 
                    time_index = time_stamp, 
                    freq=freq)
               
    def as_annual(self, year, value):
        time_stamp = timestamp_annual(year)
        return self.make_datapoint(value, time_stamp, 'a')

    def as_quarter(self, year, quarter, value):
        time_stamp = timestamp_quarter(year, quarter)
        return self.make_datapoint(value, time_stamp, 'q')
        
    def as_month(self, year, month, value):
        time_stamp = timestamp_month(year, month)
        return self.make_datapoint(value, time_stamp, 'm')
               
    def extract_values(self):
        for row in self.datarows:
            year=row.get_year()
            a_value, q_values, m_values = self.splitter_func(row.data)
            if a_value:
                yield self.as_annual(year, a_value)
            if q_values:
                for t, val in enumerate(q_values):
                    yield self.as_quarter(year, t + 1, val)
            if m_values:
                for t, val in enumerate(m_values):
                    yield self.as_month(year, t + 1, val)

import pandas as pd 
def timestamp_annual(year):
    return pd.Timestamp(year, 12, 31)

def timestamp_quarter(year, quarter):
    month = quarter * 3
    return timestamp_month(year, month) + pd.offsets.QuarterEnd()

def timestamp_month(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()


import re
COMMENT_CATCHER = re.compile("\D*(\d+[.,]?\d*)\s*(?=\d\))")

def to_float(text: str, i=0):
    """Convert *text* to float() type.

    Returns:
        Float value, or False if not successful.
    """
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



if __name__ == "__main__": # pragma: no cover
    from kep.csv2df.row_model import Row
    rows = [
        Row(['Объем ВВП, млрд.рублей / Gross domestic product, bln rubles']), 
        Row(['1999', '4823', '901', '1102', '1373', '1447'])
    ]
    tables = list(split_to_tables(rows))
    t = tables[0]
    t.set_splitter(None)
    t.varname = 'GDP'
    t.unit = 'bln_rub'
    datapoints = list(t.extract_values())
    assert datapoints == \
    [{'freq': 'a',
      'label': 'GDP_bln_rub',
      'time_index': pd.Timestamp('1999-12-31'),
      'value': 4823},
     {'freq': 'q',
      'label': 'GDP_bln_rub',
      'time_index': pd.Timestamp('1999-06-30'),
      'value': 901},
     {'freq': 'q',
      'label': 'GDP_bln_rub',
      'time_index': pd.Timestamp('1999-09-30'),
      'value': 1102},
     {'freq': 'q',
      'label': 'GDP_bln_rub',
      'time_index': pd.Timestamp('1999-12-31'),
      'value': 1373},
     {'freq': 'q',
      'label': 'GDP_bln_rub',
      'time_index': pd.Timestamp('2000-03-31'),
      'value': 1447}]
    

