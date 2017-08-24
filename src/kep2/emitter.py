"""Emitting values from list of tables."""

import re
import warnings

from datetime import date
import calendar

import pandas as pd


__all__ = ['Emitter']


# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)


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

class DatapointMaker:
    
    def __init__(self, year, label):
        self.year = year
        self.label = label
        self.freq = False
        self.value = False
        self.period = False 
    
    def set_value(self, x):
        if x: 
            self.value = to_float(x)
        else:
            self.value = None            

    def make(self, freq: str, x: float, period=False):
        self.freq = freq
        self.set_value(x)
        self.period = period
        return self.as_dict()

    def get_date(self):
        if self.freq=='a':
            return pd.Timestamp(self.year) + pd.offsets.YearEnd()
        elif self.freq=='q':
            return get_date_quarter_end(self.year, self.period)
        elif self.freq=='m':
            return get_date_month_end(self.year, self.period)
            
    def as_dict(self):
        basedict = dict(year=int(self.year),
                        label=self.label,
                        freq=self.freq,
                        value=self.value,
                        time_index=self.get_date())
        if self.freq == 'q':
            basedict.update(dict(qtr=self.period))
        elif self.freq == 'm':
            basedict.update(dict(month=self.period))
        return basedict 

class DictMaker:
    def __init__(self, year, label):
        self.basedict = {'year': year, 'label': label}

    def a_dict(self, val):
        return {**self.basedict, 'freq': 'a', 'value': to_float(val)}

    def q_dict(self, val, q):
        return {**self.basedict, 'freq': 'q', 'value': to_float(val), 'qtr': q}

    def m_dict(self, val, m):
        return {
            **self.basedict,
            'freq': 'm',
            'value': to_float(val),
            'month': m}

    def __str__(self):
        return self.basedict.__str__()


# dataframe dates handling

def _month_end_day(year, month):
    return calendar.monthrange(year, month)[1]


def get_date_month_end(year, month):
    day = _month_end_day(year, month)
    return pd.Timestamp(date(year, month, day))


def get_date_quarter_end(year, qtr):
    # quarter number should be based at 1
    assert qtr <= 4 and qtr >= 1
    month = qtr * 3
    return get_date_month_end(year, month)


def get_date_year_end(year):
    return pd.Timestamp(date(year, 12, 31))


class Emitter:
    """Emitter extractsand emits annual, quarterly and monthly values
       from a list Table() instances.

       Methods:
           .get_dataframe(freq)

       Raises:
           ValueError if any table in list is not defined.

       Method:
           get_dataframe(freq)
    """
    
    @staticmethod
    def _assert_defined(table):
        if not table.is_defined():
            raise ValueError("Undefined table:\n{}".format(table))

    def __init__(self, tables):
        self.a = []
        self.q = []
        self.m = []
        for t in tables:
            self._assert_defined(t)    
            self._import(t)

    def _import(self, table):
        for row in table.datarows:
            factory = DatapointMaker(row.get_year(), table.label)
            a_value, q_values, m_values = table.splitter_func(row.data)
            if a_value:
                self.a.append(factory.make('a', a_value))
            if q_values:
                qs = [factory.make('q', val, t + 1)
                      for t, val in enumerate(q_values) if val]
                self.q.extend(qs)
            if m_values:
                ms = [factory.make('m', val, t + 1)
                      for t, val in enumerate(m_values) if val]
                self.m.extend(ms)

    def _collect(self, freq):
        if freq in "aqm":
            return dict(a=self.a, q=self.q, m=self.m)[freq]
        else:
            raise ValueError(freq)

    @staticmethod
    def assert_has_no_duplicate_rows(df):
        if df.empty:
            dups = df
        else:
            dups = df[df.duplicated(keep=False)]
        if not dups.empty:           #
            raise ValueError("Duplicate rows found {}".format(dups))

    
    
    def get_dataframe(self, freq):
        df = pd.DataFrame(self._collect(freq))
        if df.empty:
            return pd.DataFrame()
        self.assert_has_no_duplicate_rows(df)
        # reshape
        df = df.pivot(columns='label', values='value', index='time_index')
        # add year and period
        df.insert(0, "year", df.index.year)
        if freq == "q":
            df.insert(1, "qtr", df.index.quarter)
        elif freq == "m":
            df.insert(1, "month", df.index.month)
        # delete some df internals for better view
        df.columns.name = None
        df.index.name = None
        return df

# ------------------------

from kep2.parcer import Table

labels = {0:'GDP_bln_rub',
          1:'GDP_rog',
          2:'INDPRO_yoy'}

parsed_varnames = {0:'GDP',
            1:'GDP',
            2:'INDPRO'}

parsed_units = {0:'bln_rub',
                1:'rog',
                2:'yoy'}

headers = {0: [Row(['Объем ВВП', '', '', '', '']),
               Row(['млрд.рублей', '', '', '', ''])],
           1: [Row(['Индекс ВВП, в % к прошлому периоду/ GDP index, percent'])],
           2: [Row(['Индекс промышленного производства']),
               Row(['в % к соответствующему периоду предыдущего года'])]
           }

data_items = {0: [Row(["1991", "4823", "901", "1102", "1373", "1447"])],
              1: [Row(['1991', '106,4', '98,1', '103,1', '111,4', '112,0'])],
              2: [Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]
              }


class Sample:
    """Fixtures for testing"""
    def rows(i):
        return headers[i] + data_items[i]

    def headers(i):
        return headers[i]

    def data_items(i):
        return data_items[i]

    def table(i):
        return Table(headers[i], data_items[i])
    
    def table_parsed(i):
        t = Table(headers[i], data_items[i])
        t.varname = parsed_varnames[i]
        t.unit = parsed_units[i]        
        t.set_splitter(funcname=None)
        return t

    def label(i):
        return labels[i]

#-------------------------

tables = [Sample.table_parsed(0), Sample.table_parsed(1)]
e = Emitter(tables)
df = e.get_dataframe('q')

assert df.to_dict(orient='index') == {
 pd.Timestamp('1991-03-31'): {'GDP_bln_rub': 901.0,
  'GDP_rog': 98.1,
  'qtr': 1,
  'year': 1991},
 pd.Timestamp('1991-06-30'): {'GDP_bln_rub': 1102.0,
  'GDP_rog': 103.1,
  'qtr': 2,
  'year': 1991},
 pd.Timestamp('1991-09-30'): {'GDP_bln_rub': 1373.0,
  'GDP_rog': 111.4,
  'qtr': 3,
  'year': 1991},
 pd.Timestamp('1991-12-31'): {'GDP_bln_rub': 1447.0,
  'GDP_rog': 112.0,
  'qtr': 4,
  'year': 1991}}