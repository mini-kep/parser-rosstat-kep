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

from kep.rows import read_csv, to_rows, open_csv
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
        if not table.is_defined():
            raise ValueError("Undefined table:\n{}".format(table))
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

    def get_dataframe(self, freq):
        df = pd.DataFrame(self.collect_data(freq))
        if df.empty:
            return df
        self.no_duplicate_rows(df)
        funcs = dict(a=lambda x: get_date_year_end(x['year']),
                     q=lambda x: get_date_quarter_end(x['year'], x['qtr']),
                     m=lambda x: get_date_month_end(x['year'], x['month']))
        df["time_index"] = df.apply(funcs[freq], axis=1)
        df = df.pivot(columns='label', values='value', index='time_index')
        df.insert(0, "year", df.index.year)
        if freq == "q":
            df.insert(1, "qtr", df.index.quarter)
        elif freq == "m":
            df.insert(1, "month", df.index.month)
        df.columns.name = None
        df.index.name = None
        return df

    @staticmethod
    def no_duplicate_rows(df):
        if df.empty:
            dups = df
        else:
            dups = df[df.duplicated(keep=False)]
        if not dups.empty:           #
            raise ValueError("Duplicate rows found {}".format(dups))


def csvfile_to_dataframes(csvfile, spec=SPEC):
    rows = to_rows(csvfile)
    tables = get_tables(rows, spec)
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq="a")
    dfq = emitter.get_dataframe(freq="q")
    dfm = emitter.get_dataframe(freq="m")
    return dfa, dfq, dfm


VALID_DATAPOINTS = [
    dict(
        label='GDP_bln_rub', year=1999, a=4823.0), dict(
            label='GDP_bln_rub', year=1999, q={
                4: 1447}), dict(
                    label='GDP_yoy', year=1999, a=106.4), dict(
                        label='EXPORT_GOODS_bln_usd', year=1999, m={
                            12: 9.7}), dict(
                                label='IMPORT_GOODS_bln_usd', year=1999, m={
                                    12: 4.0}), dict(
                                        label='CPI_rog', year=1999, a=136.5), dict(
                                            label='CPI_rog', year=1999, q={
                                                1: 116.0, 2: 107.3, 3: 105.6, 4: 103.9}), dict(
                                                    label='CPI_rog', year=1999, m={
                                                        1: 108.4, 6: 101.9, 12: 101.3})]


class Validator():

    def __init__(self, dfa, dfq, dfm):
        self.dfa = dfa
        self.dfq = dfq
        self.dfm = dfm

    def must_include(self, pt):
        not_included = list(self.missing_datapoints(pt))
        if not_included:
            msg = "Not found in dataset: {}".format(not_included)
            raise ValueError(msg)

    def missing_datapoints(self, pt):
        label = pt['label']
        year = pt['year']
        if 'a' in pt.keys():
            a = pt['a']
            if self.get_value(self.dfa, label, year) != a:
                yield dict(label=label, year=year, a=a)
        if 'q' in pt.keys():
            for q, val in pt['q'].items():
                if self.get_value(self.dfq, label, year, qtr=q) != val:
                    yield dict(label=label, year=year, q={q: val})
        if 'm' in pt.keys():
            for m, val in pt['m'].items():
                if self.get_value(self.dfm, label, year, month=m) != val:
                    yield dict(label=label, year=year, q={q: val})

    @staticmethod
    def get_value(df, label, year, qtr=False, month=False):
        try:
            df = df[df['year'] == year]
            ix = df.year == year  # FIXME: just all True values
            if qtr:
                ix = df['qtr'] == qtr
            if month:
                ix = df['month'] == month
            return df[ix][label][0]
        except KeyError:
            return False


def filter_date(year, month):
    # set to latest date if omitted
    latest_year, latest_month = get_latest_date()
    return year or latest_year, month or latest_month


class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year=False, month=False):
        self.year, self.month = filter_date(year, month)
        csv_path = locate_csv(self.year, self.month)
        with open_csv(csv_path) as csvfile:
            self.dfa, self.dfq, self.dfm = csvfile_to_dataframes(csvfile)

    def dfs(self):
        """Shorthand for obtaining three dataframes."""
        return self.dfa, self.dfq, self.dfm

    def save(self):
        folder_path = get_processed_folder(self.year, self.month)
        self.dfa.to_csv(folder_path / 'dfa.csv')
        self.dfq.to_csv(folder_path / 'dfq.csv')
        self.dfm.to_csv(folder_path / 'dfm.csv')
        print("Saved dataframes to", folder_path)

    def validate(self):
        v = Validator(self.dfa, self.dfq, self.dfm)
        for pt in VALID_DATAPOINTS:
            v.must_include(pt)
        print("Test values parsed OK for", self)

    def __repr__(self):
        return "Vintage ({}, {})".format(self.year, self.month)


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
        vintage.validate()

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
