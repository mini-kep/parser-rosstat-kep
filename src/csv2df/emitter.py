"""Emitting datapoints from tables."""

import re
import pandas as pd


__all__ = ['Emitter']


COMMENT_CATCHER = re.compile("\D*(\d+[.,]?\d*)\s*(?=\d\))")


def to_float(text: str, i=0):
    """Convert *text* to float() type.

    Returns:
        Float value, or False if not sucessful.
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


class DatapointMaker:
    """Factory to make dictionaries representing a datapoint."""

    def __init__(self, year, label):
        self.year = year
        self.label = label
        self.freq = False
        self.value = False
        self.period = False

    def set_value(self, x):
        if x:  # (ID) if x can have value of 0 then `else` will be executed.
            self.value = to_float(x)
        else:
            self.value = None

    def make(self, freq: str, x: float, period=False):
        self.freq = freq
        self.set_value(x)
        self.period = period
        return self.as_dict()

    def get_date(self):
        # annual
        if self.freq == 'a':
            return pd.Timestamp(str(self.year)) + pd.offsets.YearEnd()
        # qtr
        year = int(self.year)
        if self.freq == 'q':
            month = int(self.period) * 3
            base = pd.Timestamp(year, month, 1)
            return base + pd.offsets.QuarterEnd()
        #  month
        elif self.freq == 'm':
            month = int(self.period)
            base = pd.Timestamp(year, month, 1)
            return base + pd.offsets.MonthEnd()

    def as_dict(self):
        # FIXME: whu do we need year, qtr and month here?
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



def import_table_values_by_frequency(tables):
    a = []
    q = []
    m = []
    for table in tables:
        # safeguard - all tables must be definaed at this point
        if not table.is_defined():
            raise ValueError('Undefined table:\n{}'.format(table))
        splitter = table.splitter_func
        for row in table.datarows:
            factory = DatapointMaker(row.get_year(), table.label)            
            a_value, q_values, m_values = splitter(row.data)
            if a_value:
                a.append(factory.make('a', a_value))
            if q_values:
                qs = [factory.make('q', val, t + 1)
                      for t, val in enumerate(q_values) if val]
                q.extend(qs)
            if m_values:
                ms = [factory.make('m', val, t + 1)
                      for t, val in enumerate(m_values) if val]
                m.extend(ms)
    return a, q, m                 
            
class Emitter:
    """Emitter extractsand emits annual, quarterly and monthly values
       from a list Table() instances.

       Methods:
           .get_dataframe(freq)

       Raises:
           ValueError if any table in list is not defined.

    """

#    @staticmethod
#    def _assert_defined(table):
#        if not table.is_defined():
#            raise ValueError("Undefined table:\n{}".format(table))

    def __init__(self, tables):
        a, q, m = import_table_values_by_frequency(tables)
        self.selector = dict(a=a, q=q, m=m)
        
#        self.a = []
#        self.q = []
#        self.m = []
#        for t in tables:
#            self._assert_defined(t)
#            self._import(t)
#
#    def _import(self, table):
#        for row in table.datarows:
#            factory = DatapointMaker(row.get_year(), table.label)
#            a_value, q_values, m_values = table.splitter_func(row.data)
#            if a_value:
#                self.a.append(factory.make('a', a_value))
#            if q_values:
#                qs = [factory.make('q', val, t + 1)
#                      for t, val in enumerate(q_values) if val]
#                self.q.extend(qs)
#            if m_values:
#                ms = [factory.make('m', val, t + 1)
#                      for t, val in enumerate(m_values) if val]
#                self.m.extend(ms)
#
#    def _collect(self, freq):
#        if freq in "aqm":
#            return dict(a=self.a, q=self.q, m=self.m)[freq]
#        else:
#            raise ValueError(freq)
#
#    @staticmethod
#    def _assert_has_no_duplicate_rows(df):
#        dups = get_duplicates(df)
#        if not dups.empty:
#            raise ValueError("Duplicate rows found {}".format(dups))

    def get_dataframe(self, freq):        
        df = pd.DataFrame(self.selector[freq])
        if df.empty:
            return pd.DataFrame()
        # check for duplicates
        dups = get_duplicates(df)
        if not dups.empty:
            raise ValueError("Duplicate rows found {}".format(dups))
        # reshape
        df = df.pivot(columns='label', values='value', index='time_index')
        # add year and period
        df.insert(0, "year", df.index.year)
        if freq == "q":
            df.insert(1, "qtr", df.index.quarter)
        if freq == "m":
            df.insert(1, "month", df.index.month)
        # delete some df internals for better view
        df.columns.name = None
        df.index.name = None
        # --------------------------------------------
        # this is injection point of df transomations
        
        # df tranfromations go here
        
        # --------------------------------------------
        return df

def get_duplicates(df):
    if df.empty:
        return df
    else:
        return df[df.duplicated(keep=False)]       
    

if __name__ == '__main__':       
    from csv2df.parser import get_tables
    tables = get_tables(2017, 10)
    e = Emitter(tables)
    dfa = e.get_dataframe('a')
    dfq = e.get_dataframe('q')
    dfm = e.get_dataframe('m')
    a, q, m = import_table_values_by_frequency(tables)
