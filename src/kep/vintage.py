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
from kep.files import locate_csv, get_processed_folder, filled_dates
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
            self.add_table(t)

    def add_table(self, table):
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

# FIXME: may create Validator class
#
#   def get(self, freq, label=None, year=None):
#        gen = self.emit_by_freq(freq)
#        if label:
#            gen = filter(lambda x: x['label'].startswith(label), gen)
#        if year:
#            gen = filter(lambda x: x['year'] == year, gen)
#        return list(gen)


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

    def __init__(self, tables):
        self.emitter = Emitter(t for t in tables if t.is_defined())
        self.datapoints = [x for freq in "aqm"
                           for x in self.emitter.collect_data(freq)]

        dfa = pd.DataFrame(self.emitter.collect_data("a"))
        dfq = pd.DataFrame(self.emitter.collect_data("q"))
        dfm = pd.DataFrame(self.emitter.collect_data("m"))
        for df in dfa, dfq, dfm:
            self.validate(df)
        self.dfa = self.reshape_a(dfa)
        self.dfq = self.reshape_q(dfq)
        self.dfm = self.reshape_m(dfm)

    def includes(self, x):
        return x in self.datapoints

    @staticmethod
    def validate(df):
        if not df.empty:
            dups = df[df.duplicated(keep=False)]
            if not dups.empty:
                # df must have no duplicate rows
                raise ValueError(dups)

    @staticmethod
    def reshape_a(dfa):
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
    def reshape_q(dfq):
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
    def reshape_m(dfm):
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

    def save(self, folder_path):
        self.dfa.to_csv(folder_path / 'dfa.csv')
        self.dfq.to_csv(folder_path / 'dfq.csv')
        self.dfm.to_csv(folder_path / 'dfm.csv')
        print("Saved dataframes to", folder_path)

    def dfs(self):
        """Shorthand for obtaining dataframes."""
        return self.dfa, self.dfq, self.dfm

        
        
        
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



class Vintage:
    """Represents dataset release for a given year and month."""

    def __init__(self, year, month):
        # save for reference and navigation
        self.year, self.month = year, month
        # find csv
        self.csv_path = locate_csv(year, month)
        # rowstack
        self.rows = read_csv(self.csv_path)
        # break csv to tables with variable names
        self.tables = get_tables(self.rows, spec = SPEC)
        # convert stream values to pandas dataframes
        self.frames = Frames(tables=self.tables)

    def save(self):
        """Save dataframes to CSVs."""
        processed_folder = get_processed_folder(self.year, self.month)
        self.frames.save(processed_folder)

    def dfs(self):
        """Shorthand for obtaining dataframes."""
        return self.frames.dfs()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Vintage ({}, {})".format(self.year, self.month)

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

    # TODO: need parsing result

    # some notebook work
#    iq = ["GDP_yoy", "IND_PROD_yoy", "INVESTMENT_yoy", "RETAIL_SALES_yoy", "WAGE_REAL_yoy"]
#    last_q = dfq[iq]['2017-03'].transpose()
#    im = [           "IND_PROD",                       "RETAIL_SALES",     "WAGE_REAL"]
#    im1 = ["{}_yoy".format(x) for x in im]
#    last_m1 = dfm[im1]['2017-05'].transpose()
#    im2 = ["{}_rog".format(x) for x in im]
#    last_m2 = dfm[im2]['2017-05'].transpose()
    # print(last_m1)
    # print(last_m2)

    # TODO:
    # all_names = set(dfa.columns + dfq.columns + dfm.columns)

    #from kep.tables import extract_varname
#    print("Всего переменных: {}".format(len(list(cfg.SPEC.required()))))
#    for k, v in cfg.SECTIONS.items():
#        print("\n**{}**:".format(k))
#        for vn in v:
#            z = []
#            for x in cfg.SPEC.required():
#                if x[0] == vn:
#                    z.append(x[1])
#            print("- {}({})".format(vn, ", ".join(z)))
