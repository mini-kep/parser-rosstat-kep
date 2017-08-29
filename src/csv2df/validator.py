# -*- coding: utf-8 -*-
"""Use hardcoded constants for year 1999 to validate dfa, dfq, dfm dataframes.
   These dataframes are the result of parsign procedure.

   Hardcoded constants are recorded in ANNUAL, QTR and MONTHLY variables,
   converted to dictionaries using *serialise()*. CHECKPOINTS holds all
   sample datapoints as dictionaries.

   Validator(dfa, dfq, dfm).run() tests dataframes against CHECKPOINTS.
"""


__all__ = []  # TODO: (ID) Which classes/functions need to be added to __all__?


ANNUAL = [('a', 'GDP_bln_rub', 1999, 4823.0),
          ('a', 'GDP_yoy', 1999, 106.4)
          ]


QTR = [('q', 'GDP_bln_rub', 1999, {4: 1447}),
       ('q', 'CPI_rog', 1999, {1: 116.0, 2: 107.3, 3: 105.6, 4: 103.9})
       ]


MONTHLY = [('m', 'CPI_rog', 1999, {1: 108.4, 6: 101.9, 12: 101.3}),
           ('m', 'EXPORT_GOODS_bln_usd', 1999, {12: 9.7}),
           ('m', 'IMPORT_GOODS_bln_usd', 1999, {12: 4.0})
           ]


def serialise(checkpoint):
    out = dict(freq=checkpoint[0],
               label=checkpoint[1],
               year=checkpoint[2],
               period=False,
               value=False)
    val = checkpoint[3]
    if isinstance(val, dict):
        for k, v in val.items():
            cur_out = out.copy()
            cur_out.update(dict(period=k, value=v))
            yield cur_out
    else:
        out.update(dict(value=val))
        yield out


CHECKPOINTS = [pt for c in ANNUAL + QTR + MONTHLY for pt in serialise(c)]


class Validator():

    def __init__(self, dfa, dfq, dfm, checkpoints=False):
        self.dfa = dfa
        self.dfq = dfq
        self.dfm = dfm
        if checkpoints:
            self.checkpoints = checkpoints
        else:
            self.checkpoints = CHECKPOINTS

    def get_annual_value(self, label, year):
        return self.dfa[self.dfa.year == year][label].iloc[0]

    def get_qtr_value(self, label, year, qtr):
        df = self.dfq
        return df[(df.year == year) & (df.qtr == qtr)][label].iloc[0]

    def get_monthly_value(self, label, year, month):
        df = self.dfm
        return df[(df.year == year) & (df.month == month)][label].iloc[0]

    def get_value(self, pt):
        freq = pt['freq']
        label, year = pt['label'], pt['year']
        if freq == "a":
            return self.get_annual_value(label, year)
        elif freq == "q":
            qtr = pt['period']
            return self.get_qtr_value(label, year, qtr)
        elif freq == "m":
            month = pt['period']
            return self.get_monthly_value(label, year, month)
        else:
            raise ValueError(freq)

    def is_included(self, pt):
        return pt['value'] == self.get_value(pt)

    def run(self):
        not_included = [p for p in self.checkpoints if not self.is_included(p)]
        if not_included:
            msg = "Not found in dataset: {}".format(not_included)
            raise ValueError(msg)
