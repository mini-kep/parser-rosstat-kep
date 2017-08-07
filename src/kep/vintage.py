"""Create pandas dataframes based on data in Table() instances.


*Emitter* class extracts data at different frequences from Table.datarows
          from a list of Table() instances.
*Frames* uses Emitter.collect_data() method to get data, creates pandas dataframes
*Vintage* is a wrapper class to create and save dataframes based on year and month.


Main call:

   Vintage(year, month).save()


"""

import re
import warnings

from datetime import date
import calendar

import pandas as pd

from kep.rows import read_csv
from kep.files import locate_csv, get_processed_folder, filled_dates, get_latest_date
from kep.tables import get_tables
from kep.spec import SPEC



# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)

# Emitting values from Tables

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


class Emitter:
    """Emitter extracts, holds and emits annual, quarterly and monthly values
       from list of defined Table() instances.
    """

    def __init__(self, tables):
        self.a = []
        self.q = []
        self.m = []
        for t in tables:
            self._add_table(t)

    def _add_table(self, table):
        # defined Table() must have *label* and *splitter_func*
        if not table.is_defined():
            raise ValueError(table)
        for row in table.datarows:
            dmaker = DictMaker(row.get_year(), table.label)
            a_value, q_values, m_values = table.splitter_func(row.data)
            if a_value:
                self.a.append(dmaker.a_dict(a_value))
            if q_values:
                qs = [dmaker.q_dict(val, t + 1)
                      for t, val in enumerate(q_values) if val]
                self.q.extend(qs)
            if m_values:
                ms = [dmaker.m_dict(val, t + 1)
                      for t, val in enumerate(m_values) if val]
                self.m.extend(ms)

    def collect_data(self, freq):
        if freq in "aqm":
            return getattr(self, freq)
        else:
            raise ValueError(freq)
            
    def get_all_datapoints(self):
        """Iterate over all frequencies and make return list of datapoints"""
        # concat three lists
        return  [x for freq in "aqm"
                   for x in self.collect_data(freq)]


   


# dataframe dates handling


def month_end_day(year, month):
    return calendar.monthrange(year, month)[1]


def get_date_month_end(year, month):
    day = month_end_day(year, month)
    return pd.Timestamp(date(year, month, day))


def get_date_quarter_end(year, qtr):
    # quarter number should be based at 1
    assert qtr <= 4 and qtr >= 1
    month = qtr * 3
    return get_date_month_end(year, month)


def get_date_year_end(year):
    return pd.Timestamp(date(year, 12, 31))


def make_dataframes(tables):
    return DataframeMaker(tables).get_dataframes()

    
class DataframeMaker(object):
    """Create pandas DataFrames.
    
    Public method:        
      -  get_dataframes()

    """

    def __init__(self, tables):
        self.emitter = Emitter(t for t in tables if t.is_defined())
        dfa = pd.DataFrame(self.emitter.collect_data("a"))
        dfq = pd.DataFrame(self.emitter.collect_data("q"))
        dfm = pd.DataFrame(self.emitter.collect_data("m"))
        for df in dfa, dfq, dfm:
            self._validate(df)
        self.dfa = self._reshape_a(dfa)
        self.dfq = self._reshape_q(dfq)
        self.dfm = self._reshape_m(dfm)
        
    def get_dataframes(self):
        return self.dfa, self.dfq, self.dfm 
    
    @staticmethod
    def _get_duplicate_rows(df):
        if df.empty:
            return df
        else:
            return df[df.duplicated(keep=False)]
                
    def _validate(self, df):
        dups = self._get_duplicate_rows(df)
        if not dups.empty:           # 
           raise ValueError("Duplicate rows found {}".format(dups))

    @staticmethod
    def _reshape_a(dfa):
        """Returns pandas dataframe with ANNUAL data."""
        dfa["time_index"] = dfa.apply(
            lambda x: get_date_year_end(
                x['year']), axis=1)
        dfa = dfa.pivot(columns='label', values='value', index='time_index')
        dfa.insert(0, "year", dfa.index.year)
        dfa.columns.name = None
        dfa.index.name = None
        return dfa

    @staticmethod
    def _reshape_q(dfq):
        """Returns pandas dataframe with QUARTERLY data."""
        dfq["time_index"] = dfq.apply(
            lambda x: get_date_quarter_end(
                x['year'], x['qtr']), axis=1)
        dfq = dfq.pivot(columns='label', values='value', index='time_index')
        dfq.insert(0, "year", dfq.index.year)
        dfq.insert(1, "qtr", dfq.index.quarter)
        dfq.columns.name = None
        dfq.index.name = None
        return dfq

    @staticmethod
    def _reshape_m(dfm):
        """Returns pandas dataframe with MONTHLY data."""
        dfm["time_index"] = dfm.apply(
            lambda x: get_date_month_end(
                x['year'], x['month']), axis=1)
        dfm = dfm.pivot(columns='label', values='value', index='time_index')
        dfm.insert(0, "year", dfm.index.year)
        dfm.insert(1, "month", dfm.index.month)
        dfm.columns.name = None
        dfm.index.name = None
        return dfm



class DataframeHolder(object):

    def __init__(self, dfa, dfq, dfm):
        self.dfa = dfa
        self.dfq = dfq
        self.dfm = dfm

    def annual(self):
        return self.dfa

    def quarterly(self):
        return self.dfq

    def monthly(self):
        return self.dfm

    def dfs(self):
        """Shorthand for obtaining all three dataframes."""
        return self.dfa, self.dfq, self.dfm  

    # TODO: need new validation procedure
    def includes(self, x):
        return True

    def save(self, year, month):
        folder_path = get_processed_folder(year, month)
        self.dfa.to_csv(folder_path / 'dfa.csv')
        self.dfq.to_csv(folder_path / 'dfq.csv')
        self.dfm.to_csv(folder_path / 'dfm.csv')
        print("Saved dataframes to", folder_path)
        

def csv2frames(csv_path, spec=SPEC):
    # Row() instances
    rows = read_csv(csv_path)
    # convert Row() to Table()
    tables = get_tables(rows, spec)    
    # extract dataframces 
    dfa, dfq, dfm =  DataframeMaker(tables).get_dataframes()
    return DataframeHolder(dfa, dfq, dfm)

# TODO: need new validation procedure
#    def includes(self, x):
#        return x in self.datapoints   


VALID_DATAPOINTS = [
    {'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
    {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999},
    {'freq': 'a', 'label': 'EXPORT_GOODS_bln_usd', 'value': 75.6, 'year': 1999},
    {'freq': 'q', 'label': 'IMPORT_GOODS_bln_usd',
        'qtr': 1, 'value': 9.1, 'year': 1999},
    {'freq': 'a', 'label': 'CPI_rog', 'value': 136.5, 'year': 1999},
    {'freq': 'm', 'label': 'CPI_rog', 'value': 108.4, 'year': 1999, 'month': 1}
    # FIXME: found only in latest, need some monthly value
    #{'freq': 'm', 'label': 'IND_PROD_yoy', 'month': 4, 'value': 102.3, 'year': 2017}
]


# TODO: need new validation procedure


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year=False, month=False):
        # set to latest date if omitted
        latest_year, latest_month = get_latest_date()
        self.year, self.month = year or latest_year, month or latest_month
        # find csv file
        csv_path = locate_csv(self.year, self.month)
        # make dataframes
        self.df_holder = csv2frames(csv_path)

    def save(self):
        """Save dataframes to CSVs."""
        self.frames.save(self.year, self.month)

    def dfs(self):
        """Shorthand for obtaining dataframes."""
        return self.df_holder.dfs()

    def __repr__(self):
        return "Vintage ({}, {})".format(self.year, self.month)

    # TODO: need new validation procedure
    def validate(self, valid_datapoints=VALID_DATAPOINTS):
        for x in valid_datapoints:
            if not self.frames.includes(x):
                msg = "Not found in dataset: {}\nFile: {}".format(
                    x, self.csv_path)
                raise ValueError(msg)
        print("Test values parsed OK for", self)
     



class Collection:
    """Methods to manipulate entire set of data releases."""

    @staticmethod
    def save_all_dataframes_to_csv():
        for (year, month) in filled_dates():
            Vintage(year, month).save()

    @staticmethod
    def save_latest():
        vintage = Vintage(year=None, month=None)
        vintage.save()

    @staticmethod
    def approve_latest():
        """Quick check for algorithm on latest available data."""
        vintage = Vintage(year=None, month=None)
        #vintage.validate()

    @staticmethod
    def approve_all():
        """Checks all dates, runs slow (about 20 sec.)
           May fail if dataset not complete.
        """
        for (year, month) in filled_dates():
            vintage = Vintage(year, month)
            vintage.validate()


if __name__ == "__main__":
    Collection.approve_latest()
    # Collection.approve_all()
    # Collection.save_latest()
    # Collection.save_all_dataframes_to_csv()

    year, month = 2017, 5
    vint = Vintage(year, month)
    dfa, dfq, dfm = vint.dfs()

    # TODO: some notebook work
#    iq = ["GDP_yoy", "IND_PROD_yoy", "INVESTMENT_yoy", "RETAIL_SALES_yoy", "WAGE_REAL_yoy"]
#    last_q = dfq[iq]['2017-03'].transpose()
#    im = [           "IND_PROD",                       "RETAIL_SALES",     "WAGE_REAL"]
#    im1 = ["{}_yoy".format(x) for x in im]
#    last_m1 = dfm[im1]['2017-05'].transpose()
#    im2 = ["{}_rog".format(x) for x in im]
#    last_m2 = dfm[im2]['2017-05'].transpose()

