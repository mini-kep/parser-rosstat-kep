"""Parse CSV text *csv_segment* using parsing definition *pdef*:

   extract_tables(csv_segment, pdef)
"""

from collections import OrderedDict as odict
from enum import Enum, unique
import pandas as pd

import kep.csv2df.util.row_splitter as splitter
from kep.csv2df.row_model import Row
from kep.csv2df.row_stack import text_to_list
from kep.csv2df.util.label import make_label
from kep.csv2df.util.to_float import to_float

__all__ = ['extract_tables']


def extract_tables(csv_segment: str, pdef):
    """Extract tables from *csv_segment* string using *pdef* parsing defintion.

    Args:
        csv_segment(str): CSV text
        pdef: parsing defintion with search strings for header and unit

    Returns:
        list of Table() instances    
    """
    tables = split_to_tables(csv_segment)
    tables = parse_tables(tables, pdef)
    verify_tables(tables, pdef)
    # there can be more tables than required, occasionally
    return [t for t in tables if t.label in pdef.required]


def parse_tables(tables, pdef):
    # assign reader function
    # parse tables to obtain labels - set label and splitter
    for t in tables:
        t.set_splitter(pdef.reader)
        t.set_label(pdef.mapper, pdef.units)        
    # assign trailing units
    # for tables without *varname* - copy *varname* from previous table.
    for prev_table, table in zip(tables, tables[1:]):
        if table.varname is None and not table.has_unknown_lines():
            table.varname = prev_table.varname
    return tables


def verify_tables(tables, pdef):
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in pdef.required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels: {}".format(labels_missed))

@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2


def split_to_tables(rows):
    """Yields Table() instances from *rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        r = Row(row)
        if r.is_datarow():
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:  
                # table ended, emit it
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.HEADERS
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class HeaderParsingProgress:
    def __init__(self, headers):
        self.lines = [Row(line).name for line in headers]
        self.is_known = {line: False for line in self.lines}

    def set_as_known(self, line):
        self.is_known[line] = True     

    def is_parsed(self):
        return all(self.is_known.values())
    
    @property
    def printable(self):
        def sym(line):
            return {True: "+", False: "-"}[self.is_known[line]] 
        return ['{} <{}>'.format(sym(line), line) for line in self.lines]
        
    def __str__(self):    
        return '\n'.join(self.printable)


# TODO: convert to unit test    
progress = HeaderParsingProgress([['abc', 'zzz'], ['def', '...']])
assert progress.is_parsed() is False
progress.set_as_known('abc') 
progress.set_as_known('def') 
assert progress.is_parsed() is True
assert '<abc>' in str(progress)


class Table:
    """Representation of CSV table, has headers and datarows."""

    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows
        # parsing
        self.splitter_func = None
        self.varname = None
        self.unit = None
        self.datapoints = []
        # prasing progress indicator
        self.progress = HeaderParsingProgress(headers)

    @property
    def coln(self):
        """Number of columns in table."""
        return max(len(Row(row)) for row in self.datarows)

    def set_label(self, varnames_dict, units_dict):
        for row in self.headers:
            r = Row(row)
            varname = r.get_varname(varnames_dict)
            if varname:
                self.varname = varname
                self.progress.set_as_known(r.name)
            unit = r.get_unit(units_dict)
            if unit:
                self.unit = unit
                self.progress.set_as_known(r.name)

    def set_splitter(self, reader):
        key = reader or self.coln
        self.splitter_func = splitter.get_splitter(key)

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
        return not self.progress.is_parsed()

    def __eq__(self, x):
        return self.headers == x.headers and self.datarows == x.datarows

    def __str__(self):
        def join(items):
            return '\n'.join([str(x) for x in items])
        _title = "Table {} ({} columns)".format(self.label, self.coln)
        _header = join(self.progress.printable)
        _data = join(self.datarows)
        return join([_title, _header, _data])

    def __repr__(self):
        return "Table(\n    headers={},\n    datarows={})" \
               .format(repr(self.headers), repr(self.datarows))

    def make_datapoint(self, value: str, time_stamp, freq):
        return dict(label=self.label,
                    value=to_float(value),
                    time_index=time_stamp,
                    freq=freq)

    def extract_values(self):
        """Yield dictionaries with variable name, frequency, time_index 
           and value.
        """
        for row in self.datarows:
            year = Row(row).year
            data = Row(row).data
            a_value, q_values, m_values = self.splitter_func(data)
            if a_value:
                time_stamp = timestamp_annual(year)
                yield self.make_datapoint(a_value, time_stamp, 'a')
            if q_values:
                for t, val in enumerate(q_values):
                    time_stamp = timestamp_quarter(year,  t + 1)
                    yield self.make_datapoint(val, time_stamp, 'q')
            if m_values:
                for t, val in enumerate(m_values):
                    time_stamp = timestamp_month(year,  t + 1)
                    yield self.make_datapoint(val, time_stamp, 'm')


def timestamp_annual(year):
    return pd.Timestamp(year, 12, 31)


def timestamp_quarter(year, quarter):
    month = quarter * 3
    return timestamp_month(year, month)


def timestamp_month(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()


if __name__ == "__main__":  # pragma: no cover
    DOC = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""
    rows = text_to_list(DOC)
    tables = list(split_to_tables(rows))
    t = tables[0]
    t.set_splitter(None)
    t.varname = 'GDP'
    t.unit = 'bln_rub'
    datapoints = list(t.extract_values())
    assert datapoints[0] == {'freq': 'a',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-12-31'),
                             'value': 4823}
    assert datapoints[1] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-03-31'),
                             'value': 901}
    assert datapoints[2] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-06-30'),
                             'value': 1102}
    assert datapoints[3] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-09-30'),
                             'value': 1373}
    assert datapoints[4] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-12-31'),
                             'value': 1447}
   
