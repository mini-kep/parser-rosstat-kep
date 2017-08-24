"""Create pandas dataframes based on data in Table() instances and save to CSV.

*Emitter* class extracts data at different frequences from Table() instances.

*Vintage* class addresses dataset by year and month:

   Vintage(year, month).validate()
   Vintage(year, month).save()

*Collection* manipulates all datasets, released at various dates:

    - save_all()
    - save_latest()
    - approve_latest()
    - approve_all()

"""

import re
import warnings

from datetime import date
import calendar

import pandas as pd

from kep.rows import to_rows, open_csv
from kep.files import locate_csv, get_processed_folder, filled_dates, get_latest_date
from kep.tables import get_tables
from kep.spec import SPEC
from kep.validator import Validator


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
       from list or stream Table() instances. Table() must be defined with
       label and splitter function.

       Raises:
           ValueError if any input table is not defined.

       Method:
           get_dataframe(freq)
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

    def _collect(self, freq):
        if freq in "aqm":
            return dict(a=self.a, q=self.q, m=self.m)[freq]
        else:
            raise ValueError(freq)

    @staticmethod
    def _assert_has_no_duplicate_rows(df):
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
        self._assert_has_no_duplicate_rows(df)
        # make time index
        funcs = dict(a=lambda x: get_date_year_end(x['year']),
                     q=lambda x: get_date_quarter_end(x['year'], x['qtr']),
                     m=lambda x: get_date_month_end(x['year'], x['month']))
        df["time_index"] = df.apply(funcs[freq], axis=1)
        # reshape
        df = df.pivot(columns='label', values='value', index='time_index')
        # add yeay and period
        df.insert(0, "year", df.index.year)
        if freq == "q":
            df.insert(1, "qtr", df.index.quarter)
        elif freq == "m":
            df.insert(1, "month", df.index.month)
        # delete some df internals for better view
        df.columns.name = None
        df.index.name = None
        return df


def csvfile_to_dataframes(csvfile, spec=SPEC):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Arg:
      csvfile (file connection or StringIO) - CSV file for parsing
      spec (spec.Specification) - pasing instructions, defaults to spec.SPEC
    """
    rows = to_rows(csvfile)
    tables = get_tables(rows, spec)
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq="a")
    dfq = emitter.get_dataframe(freq="q")
    dfm = emitter.get_dataframe(freq="m")
    return dfa, dfq, dfm


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
        checker = Validator(self.dfa, self.dfq, self.dfm)
        checker.run()
        print("Test values parsed OK for", self)

    def __repr__(self):
        return "Vintage ({}, {})".format(self.year, self.month)


class Collection:
    """Methods to manipulate entire set of data releases."""

    @staticmethod
    def save_all():
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
        """Checks all dates, runs for about 1-2 min of a fast computer.
           May fail if dataset not complete, eg word2csv written only part
           of CSV file.
        """
        for year, month in filled_dates():
            print("Checking", year, month)
            vintage = Vintage(year, month)
            vintage.validate()


if __name__ == "__main__":
    # Collection calls
    Collection.approve_latest()
    # Collection.approve_all()
    # Collection.save_latest()
    # Collection.save_all()

    # sample dfa, dfq, dfm  and Vintage calls
    year, month = 2017, 5
    vint = Vintage(year, month)
    vint.validate()
    dfa, dfq, dfm = vint.dfs()
