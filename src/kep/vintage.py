"""Emit dataframes from raw CSV file represented as Tables() instances.

Main call:

   Vintage(year, month).save()

"""

import itertools
import re
import warnings

from datetime import date
import calendar

import pandas as pd

import kep.rows as rows
import kep.tables as tables
import kep.files as files



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
        return {**self.basedict, 'freq': 'm', 'value': to_float(val), 'month': m}

    def __str__(self):
        return self.basedict.__str__()


class Emitter:
    """Emitter extracts and holds annual, quarterly and monthly values
       for a given Table.

       Table must have defined *label* and *splitter_func*."""

    def __init__(self, table):
        if not table.is_defined():
            raise ValueError(table)
        self.a = []
        self.q = []
        self.m = []
        for row in table.datarows:
            dmaker = DictMaker(row.get_year(), table.label)
            a_value, q_values, m_values = table.splitter_func(row.data)
            if a_value:
                self.a.append(dmaker.a_dict(a_value))
            if q_values:
                self.q.extend([dmaker.q_dict(val, t + 1)
                               for t, val in enumerate(q_values) if val])
            if m_values:
                self.m.extend([dmaker.m_dict(val, t + 1)
                               for t, val in enumerate(m_values) if val])


class Datapoints:
    """Inspection into datapoints using emitters"""

    def __init__(self, tables):
        self.emitters = [Emitter(t) for t in tables if t.is_defined()]
        self.datapoints = (self.emit_by_freq("a") +
                           self.emit_by_freq("q") +
                           self.emit_by_freq("m"))

    def emit_by_freq(self, freq: str):
        assert freq in "aqm"
        gen = [getattr(e, freq) for e in self.emitters]
        return list(itertools.chain.from_iterable(gen))

    def get(self, freq, label=None, year=None):
        gen = self.emit_by_freq(freq)
        if label:
            gen = filter(lambda x: x['label'].startswith(label), gen)
        if year:
            gen = filter(lambda x: x['year'] == year, gen)
        return list(gen)

    def includes(self, x):
        return x in self.datapoints

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


class Frames:
    """Create pandas DataFrames."""

    def collect(self, freq):
        return [x for x in self.datapoints if x['freq'] == freq]

    @staticmethod
    def validate(df):
        if not df.empty:
            dups = df[df.duplicated(keep=False)]
            if not dups.empty:
                # df must have no duplicate rows
                raise ValueError(dups)

    def __init__(self, tables):
        self.datapoints = Datapoints(tables).datapoints
        dfa = pd.DataFrame(self.collect("a"))
        dfq = pd.DataFrame(self.collect("q"))
        dfm = pd.DataFrame(self.collect("m"))
        for df in dfa, dfq, dfm:
            self.validate(df)
        self.dfa = self.reshape_a(dfa)
        self.dfq = self.reshape_q(dfq)
        self.dfm = self.reshape_m(dfm)

    @staticmethod
    def reshape_a(dfa):
        """Returns pandas dataframe with ANNUAL data."""
        dfa["time_index"] = dfa.apply(
            lambda x: get_date_year_end(
                x['year']), axis=1)
        dfa = dfa.pivot(columns='label', values='value', index='time_index')
        dfa.insert(0, "year", dfa.index.year)
        dfa.columns.name = None
        return dfa

    @staticmethod
    def reshape_q(dfq):
        """Returns pandas dataframe with QUARTERLY data."""
        dfq["time_index"] = dfq.apply(
            lambda x: get_date_quarter_end(
                x['year'], x['qtr']), axis=1)
        dfq = dfq.pivot(columns='label', values='value', index='time_index')
        dfq.insert(0, "year", dfq.index.year)
        dfq.insert(1, "qtr", dfq.index.quarter)
        dfq.columns.name = None
        return dfq

    @staticmethod
    def reshape_m(dfm):
        """Returns pandas dataframe with MONTHLY data."""
        dfm["time_index"] = dfm.apply(
            lambda x: get_date_month_end(
                x['year'], x['month']), axis=1)
        dfm = dfm.pivot(columns='label', values='value', index='time_index')
        dfm.insert(0, "year", dfm.index.year)
        dfm.insert(1, "month", dfm.index.month)
        dfm.columns.name = None
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
    {'freq': 'q', 'label': 'IMPORT_GOODS_TOTAL_bln_usd',
        'qtr': 1, 'value': 9.1, 'year': 1999},
    # FIXME: found only in latest, need some monthly value
    #{'freq': 'm', 'label': 'IND_PROD_yoy', 'month': 4, 'value': 102.3, 'year': 2017}
]


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year, month):
        # save for reference and navigation
        self.year, self.month = files.filter_date(year, month)        
        # find csv
        self.csv_path = files.locate_csv(year, month)
        # rowstack 
        self.rowstack = rows.CSV(self.csv_path).rowstack
        # break csv to tables with variable names
        self.tables = tables.Tables(self.rowstack).get_required()
        # convert stream values to pandas dataframes
        self.frames = Frames(tables=self.tables)     


    def save(self):
        """Save dataframes to CSVs."""
        processed_folder = files.get_processed_folder(self.year, self.month)
        self.frames.save(processed_folder)

    def dfs(self):
        """Shorthand for obtaining dataframes."""
        return self.frames.dfa, self.frames.dfq, self.frames.dfm

    def __str__(self):
        return "{} {}".format(self.year, self.month)

    def __repr__(self):
        # FIXME: use self.__class__ in other __repr__()'s
        # FIXME: review __str__, and __repr__()
        return "{0!s}({1!r}, {2!r})".format(
            self.__class__, self.year, self.month)

    def validate(self, valid_datapoints=VALID_DATAPOINTS):
        for x in valid_datapoints:
            if x not in self.frames.datapoints:
                raise ValueError("Not found in dataset: {}".format(x) +
                                 "File: {}".format(self.csv_path))
        print("Test values parsed OK for", self)


class Collection:
    """Methods to manipulate entire set of data releases."""

    @staticmethod
    def save_all_dataframes_to_csv():
        for (year, month) in files.filled_dates():
            Vintage(year, month).save()

    @staticmethod
    def save_latest():
        vintage = Vintage(year=None, month=None)
        vintage.save()

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


if __name__ == "__main__":
    Collection.approve_latest()
    #Collection.save_latest()
    #Collection.approve_all()
    #Collection.save_all_dataframes_to_csv()

    year, month = 2017, 5
    vintage = Vintage(year, month)
    dfa, dfq, dfm = vintage.dfs()
