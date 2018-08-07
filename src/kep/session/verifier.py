"""Check contents of dataframes with checkpoints"""
import pandas as pd
from kep.util import iterate, load_yaml
from kep.parser.row import Datapoint


class Verifier():
    def init(self, dfa, dfq, dfm):
        self.dfs = dict(a=dfa, q=dfq, m=dfm)

    def all(self, lookup_values):
        """Require all values from strings, raise exception otherwise."""
        for v in lookup_values:
            if not self.is_found(v):
                msg = "Datapoint not found", v  # , subset(v, datapoints)
                raise AssertionError(msg)

    def any(self, lookup_values):
        """Require at least one value from strings, raise exception otherwise."""
        bools = [self.if_found(value) for value in lookup_values]
        if not any(bools):
            d = [(k, v) for k, v in zip(bools, lookup_values)]
            # , subset(lookup_values[0], datapoints)
            msg = "Datapoints not found", d
            raise AssertionError(msg)

    def which_df(self, freq):
        return self.dfs[freq]

    def is_found(self, d: Datapoint):
        df = self.which_df(d.freq)
        return is_in(d, df)


# def verify(checkpoints_source, dfa, dfq, dfm):
#    v = Verifier(dfa, dfq, dfm)
#    for method, args in get_checkpoints(checkpoints_source):
#        x = as_datapoints(args)
#        getattr(v, method)(x)

SRC = """
CPI_NONFOOD_rog:
   all:
      - m 1999  1 106.2
      - m 1999 12 101.1
      - m 2018  5 100.9
      - m 2019  1 -99.9
   any:
      - a 2015 99.2
      - a 2002 103.1
#
#INDPRO_yoy:
#   -
#     a 2015 99.2
#     a 2002 103.1
#  -  a 2015 99.2
#     a 2002 103.1
"""


def is_in(tseries, year, month, value, **kwargs):
    timestamp = ts(year, month)
    try:
        x = tseries[timestamp]
    except KeyError:
        # timestamp not in tseries index
        return False
    return x == value


def to_datapoint(string: str):
    string = string.replace('  ', ' ')
    args = string.split(' ')
    try:
        freq, year, month, value = args
    except ValueError:
        freq, year, value = args
        month = 12
    return dict(freq=freq,
                year=int(year),
                month=int(month),
                value=float(value)
                )


def extract(source_dict: dict, freq: str, method: str):
    for name, subdict in source_dict.items():
        items = subdict.get(method)
        if items:
            datapoints = [to_datapoint(item) for item in items]
            yield (name, [dp for dp in datapoints if dp['freq'] == freq])


def ts(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()


z = load_yaml(SRC)[0]
print(z)
df = pd.DataFrame({'CPI_NONFOOD_rog':
                   {ts(1999, 1): 106.2,
                    ts(1999, 2): 104.0,
                       ts(1999, 3): 103.2,
                       ts(1999, 4): 104.0,
                       ts(1999, 5): 102.7,
                       ts(1999, 6): 101.6,
                       ts(1999, 7): 101.9,
                       ts(1999, 8): 102.4,
                       ts(1999, 9): 102.7,
                       ts(1999, 10): 102.2,
                       ts(1999, 11): 101.5,
                       ts(1999, 12): 101.1,
                       ts(2018, 1): 100.3,
                       ts(2018, 2): 100.1,
                       ts(2018, 3): 100.2,
                       ts(2018, 4): 100.4,
                       ts(2018, 5): 100.9,
                       ts(2018, 6): 100.4}})

# df must be subset by frequency
y = list(extract(z, 'm', 'all'))
for name, values in y:
    tseries = df[name]
    for v in values:
        print(name, v, is_in(tseries, **v))
