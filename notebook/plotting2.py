
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt # without this, matplotlib.style.use crashes with AttributeError
from matplotlib.ticker import NullFormatter
from pandas.tseries.converter import TimeSeries_DateFormatter

# The default figsize is the size of an A4 sheet in inches
A4_SIZE_PORTRAIT = [8.27, 11.7]
TITLE_FONT_SIZE = 12

matplotlib.style.use('ggplot')

# -----------------------------------------------------
# additional formatting for plot - in PDF and png

class CustomFormatter(TimeSeries_DateFormatter):
    def __init__(self, default_formatstr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_formatstr = default_formatstr

    def _set_default_format(self, vmin, vmax):
        formatdict = super()._set_default_format(vmin, vmax)
        for loc in self.locs:
            formatdict.setdefault(loc, self.default_formatstr)
        return formatdict


def format_ax(ax):
    ax.set_xlabel('')

    # The default formatter for Pandas dataframes with dates as indices is
    # pandas.tseries.converter.TimeSeries_DateFormatter. The problem with it is
    # that it completely ignores modifications to major and minor ticks
    # and calculates all tick locations, types and labels internally by itself.
    # CustomFormatter is basically a patch that looks into the internals of
    # TimeSeries_DateFormatter and modifies whatever it has calculated so that
    # the custom tick locations are taken into account.
    major_formatter = CustomFormatter(
        default_formatstr='%Y',
        freq=ax.xaxis.get_major_formatter().freq,  # another peek into the internals
        minor_locator=False,
        dynamic_mode=True,
        plot_obj=ax
    )

    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.xaxis.set_major_formatter(major_formatter)
    
    # According to matplotlib docs, time is plotted on x-axis after converting timestamps
    # to floats using special functions in matplotlib.dates: date2num and num2date.
    # Internally, they are basically wrappers around datetime.toordinal(), which, in turn,
    # returns the number of days since January 1, year 1 (as an integer).
    # However, here get_xlim() says that the limits are the numbers of months passed since epoch.
    # For example, 348.0 is the left limit and 348/12 = 29. This matches the beginning of year
    # 1999. Hence this recalculation.
    # I haven't investigated whether this is intentional or if Pandas simply doesn't follow
    # matplotlib's guidelines. This shows up in Pandas 0.17.1.
    new_xright = (datetime.now().year + 1 - 1970) * 12
    # new_xright = (2015 + 1 - 1970) * 12
    #xright = ax.get_xlim()[1]
    #assert xright <= new_xright  # we'll know if the logic above breaks
    ax.set_xlim(right=new_xright)

    # ensuring that the last tick is major
    major_ticks = ax.get_xticks(minor=False)
    minor_ticks = ax.get_xticks(minor=True)
    if minor_ticks[-1] > major_ticks[-1]:
        last_tick = minor_ticks[-1]
        major_ticks = np.append(major_ticks, last_tick)
        minor_ticks = np.delete(minor_ticks, -1)
        ax.set_xticks(major_ticks, minor=False)
        ax.set_xticks(minor_ticks, minor=True)

    labels = ax.get_xticklabels()
    for l in labels:
        l.set_rotation('vertical')
    ax.xaxis.tick_bottom()

if __name__ == "__main__":
    import pandas as pd
    import matplotlib.pyplot as plt
    matplotlib.style.use('ggplot')
    url = ('https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/'
           'master/data/processed/latest/dfm.csv')
    dfm =  pd.read_csv(url, converters={0: pd.to_datetime}, index_col=0)
    ax = dfm.iloc[:,3:5].plot()    

    # https://stackoverflow.com/questions/24943991/change-grid-interval-and-specify-tick-labels-in-matplotlib
    major_ticks = pd.date_range('2000', '2020', freq='5Y')
    ax.set_xticks(major_ticks)
    # below dows not help to add back major labels 
    # plt.xticks(label=[t.year for t in major_ticks])
    minor_ticks = pd.date_range('1998', '2020', freq='Y')
    ax.set_xticks(minor_ticks, minor=True)
    
