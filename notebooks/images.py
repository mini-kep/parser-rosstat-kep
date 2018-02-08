# -*- coding: utf-8 -*-

import datetime
from urllib.parse import urljoin

import matplotlib.pyplot as plt
import pandas as pd
from kep.config import find_repo_root


def get_pix_folder(subfolder):
    return find_repo_root() / 'output' / 'png' / subfolder


start = datetime.date(1998, 12, 31)
end = datetime.date(2017, 12, 31)
DEFAULT_TIMERANGE = start, end

# graphics parameters in dicts

SPLINE_GPARAMS = {'timerange': DEFAULT_TIMERANGE,
                  'figsize': (2, 0.6),
                  'style': 'ggplot',
                  'facecolor': 'white',
                  'auto_x': False,
                  'axis_on': False}

INDICATOR_GPARAMS = {'timerange': DEFAULT_TIMERANGE,
                     'figsize': (5, 5),
                     'style': 'bmh',
                     'facecolor': 'white',
                     'auto_x': False,
                     'axis_on': True}

# TODO: we need some nice way to decide at what frequency
#      a time series or a dataframe and return 'a', 'q' or 'm'
#      maybe take first element of the dataframe index add
#      ofsset for month, qtr and year and see which oth them
#      hits the second element in graph


def get_frequency(ts):
    """Returns the frequency of a timeseries or dataframe.

        Args:
            ts: pd.Timeseries

        Returns:
            string
    """
    return str.lower(pd.infer_freq(ts.index))


# TO DISCUSS: if title is present, can we make it title of the chart
#             not much larger font than labels

class GraphBase:
    """Parent class for project charts (Spline, Chart and other)."""

    def __init__(self, ts, title=None, params={}):
        """
        Args:
            ts (pd.TimeSeries):
            params: chart formatting/style parameters
        """
        self.ts = ts
        self.params = params
        # nothing plotted yet
        self.fig = None
        # will overload this
        self.subfolder = ""

    @property
    def filename(self):
        """Returns:
              string
        """
        freq = get_frequency(self.ts)
        return f'{freq}_{self.ts.name}.png'

    @property
    def local_folder(self):
        """Returns:
               pathlib.Path()
        """
        return get_pix_folder(self.subfolder)

    @property
    def github_folder(self):
        """Returns:
               pathlib.Path()
        """
        base_url = "https://github.com/epogrebnyak/mini-kep/tree/master/output/png/"
        subfolder = f"{self.subfolder}/" if self.subfolder else ""
        return urljoin(base_url, subfolder)

    @property
    def path(self):
        """Returns:
              string
        """
        return str(self.local_folder / self.filename)

    def as_markdown(self):
        url = urljoin(self.github_folder, self.filename)
        return f'![{self.ts.name}]({url})'

    def plot_data(self, axes):
        # EP: rationale to separate it - drawing may be different
        #     on the same convas if self.ts is different class
        axes.plot(self.ts)

    def plot(self):
        plt.style.use(self.params['style'])
        # create figure
        fig = plt.figure(figsize=self.params['figsize'])
        # add 1 subplot and format it
        axes = fig.add_subplot(1, 1, 1, facecolor=self.params['facecolor'])
        axes.set_xlim(self.params['timerange'])
        # draw data at axis
        self.plot_data(axes)
        # format figure
        if self.params['auto_x']:
            fig.autofmt_xdate()
        if not self.params['axis_on']:
            plt.axis('off')
        self.fig = fig
        return self

    def save(self):
        if self.fig is None:
            raise ValueError('Figure is empty, call .plot() method first')
        else:
            self.fig.savefig(self.get_file_path())
        return self

    def close(self):
        plt.close()
        del self.fig
        self.fig = None


class Spline(GraphBase):
    def __init__(self, ts):
        super().__init__(ts, params=SPLINE_GPARAMS)
        self.subfolder = 'splines'


class Chart(GraphBase):
    def __init__(self, df, title=None):
        super().__init__(df, title, params=INDICATOR_GPARAMS)
        self.subfolder = 'indicator_chart'


class ChartDF(GraphBase):
    def __init__(self, df, title=None):
        super().__init__(df, title, params=INDICATOR_GPARAMS)
        self.df = df
        self.subfolder = 'dataframe_chart'

    def plot(self):
        # TODO: is it possible to replicate graph below?
        # it is a wrapper around df.plot with some resolution
        # https://github.com/epogrebnyak/data-lab/blob/565f431605b708246fa0f3323a651a747e9d9dfb/lab.py#L50-L53
        # the graph looks like this:
        # https://user-images.githubusercontent.com/11600722/29885655-42981f88-8dc0-11e7-9db4-bbcb27bab48f.png

        # ax = self.df.plot(figsize=(pix[0]/my_dpi, pix[1]/my_dpi))
        # fig = ax.get_figure()
        # fig.savefig(path, dpi = MY_DPI)
        # fig.clear()
        pass

# EP: lets keep it as experimental class with several subplots
#     it is useful for seeing how plt.style.use(self.params['style'])
#     behaves without parameters.


class ChartStack(GraphBase):
    def __init__(self, df, name=None):
        super().__init__(df, params=INDICATOR_GPARAMS)
        self.subfolder = 'temp'

    def plot(self):
        plt.style.use(self.params['style'])
        fig = plt.figure(figsize=self.params['figsize'])
        num_plots = len(self.ts.columns)
        for i in range(num_plots):
            ax = fig.add_subplot(num_plots, 1, i + 1)
            ax.plot(df.iloc[:, i])


def save_all_series(df):
    def plt(graph):
        graph.plot().save().close()
    cols = [x for x in dfm.columns if x not in ['year', 'month', 'qtr']]
    for col in cols:
        plt(Spline(col))
        plt(Chart(col))


def plot_all_dataframes():
    dfa, dfq, dfm = (access.get_dataframe(freq) for freq in 'aqm')
    save_all_series(dfa)
    save_all_series(dfq)
    save_all_series(dfm)


if __name__ == "__main__":

    from kep import access

    dfa, dfq, dfm = (access.get_dataframe(freq) for freq in 'aqm')

    ts = dfm.CPI_rog
    s = Spline(ts)
    c = Chart(ts, 'name2')

    # s.plot()
    # c.plot()

    varnames = ['RETAIL_SALES_FOOD_bln_rub',
                'RETAIL_SALES_NONFOOD_bln_rub'
                ]
    df = dfm[varnames]
    v = ChartStack(df)
    # v.plot()

    d = ChartDF(dfq[varnames])
    # d.plot

    qv = ['GDP_rog'
          'INDPRO_rog',
          'INVESTMENT_rog']

    mv = ['INDPRO_yoy',
          'TRANSPORT_FREIGHT_bln_tkm',
          'CPI_rog',
          'WAGE_REAL_rog',
          'UNEMPL_pct',
          'GOV_SURPLUS_FEDERAL_bln_rub',
          'EXPORT_GOODS_bln_usd',
          'IMPORT_GOODS_bln_usd']
    # RUR_USD_eop

    charts = [Chart(dfm[name]) for name in mv]
    md = [z.as_markdown() for z in charts]
