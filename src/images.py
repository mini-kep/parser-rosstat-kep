# -*- coding: utf-8 -*-
# will work after merge with master
from results.latest import get_dataframe

import matplotlib.pyplot as plt

dfa = get_dataframe('a')
dfq = get_dataframe('q')
dfm = get_dataframe('m')

# TODO:

# проанализировать общие элементы что нужно для рисунка (помимо просто датафрейма)
# проанализировать что общего в структре кода трех рисовалок
# сделать псеводкод класса рисовалки - чем иницилизируется, какие методы есть, есть ли состояния
# обратить внимание на то что надо отделить созданеи рисунка и его файловое храннеи
# подумать как тестировать

# описать юзеркейс - куда каждый тип рисунков пойдет
# 1. показать просто наличие показателья и его полседнее занченеи
# 2. дать более детальную картину показателя
# 3. сравнить несколкьо показатлеей вместе или сам себя со снятой сезонностью
# 2 и 3 могут иметь оди и тот же вид


# LATER:
# комбинациия графиков - дать ссылки на Business conditions и генеарцию
# презентации

# NOTE:
# src/helpers
# src/csv_maker
#      download
#      word2csv
#      csv2df
#
# src/csv_user
#     scripts
#     images
#     frontpage


# ############### #
# TO_PNG BLOCK 1: #
# ############### #

class Sparkline():
    LOCAL_FOLDER = get_root() / "output" / "png"
    GITHUB_FOLDER = \
        "https://github.com/epogrebnyak/mini-csv2df/raw/master/output/png/{}"

        def __init__(self, ts):
        self.ts = ts

    def path(self):
        return str(self.LOCAL_FOLDER / self.filename())

    def filename(self):
        return "{}_spark.png".format(self.ts.name)

    def plot(self):
        """Draw sparkline graph. Return Axes()."""
        fig = plt.figure(figsize=(2, 0.5))
        ax = fig.add_subplot(111)
        ax.plot(self.ts, 'r-')
        for _, v in ax.spines.items():
            v.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        return ax
        # here

    def save(self):
        spark(self.ts)
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(self.path())  # <----------------
        plt.close()

    def markdown(self):
        path = self.GITHUB_FOLDER.format(self.filename())
        return '![]{}'.format(path)


def make_sparks(df, save=False):
    df = df.drop(['year', 'month'], 1)
    for vn in df.columns:
        ts = df[vn]
        Sparkline(ts).save()


# ############### #
# TO_PNG BLOCK 2: #
# ############### #

from matplotlib.ticker import NullFormatter
from pandas.tseries.converter import TimeSeries_DateFormatter


matplotlib.style.use('ggplot')

# The default figsize is the size of an A4 sheet in inches
A4_SIZE_PORTRAIT = [8.27, 11.7]
TITLE_FONT_SIZE = 12


def one_plot(
        df,
        nrows=3,
        ncols=2,
        figsize=A4_SIZE_PORTRAIT,
        title_font_size=TITLE_FONT_SIZE):
    # set single plot size propotional to paper and number of plot rows/columns per page
    # WARNING: updating figsize in-place means that A4_SIZE_PORTRAIT gets modified.
    # This leads to unexpected problems.
    ax = df.plot(legend=None, figsize=(figsize[0] / ncols, figsize[1] / nrows))
    ax.set_title(df.name, fontsize=title_font_size)

    # additional formatting for plot
    format_ax(ax)
    return ax


def make_png_filename(vn, dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return os.path.join(dirpath, "%s.png" % vn)

# here


def write_png_pictures(df, folder):
    for vn in df.columns:
        # Indexing df as df[[vn]] produces a DataFrame, not a Series. Therefore,
        # it does not have a .name attribute, but it has .columns instead.
        ts = df[vn]

        # one_plot returns Axes and sets matplotlib's current figure to the plot it draws
        # try:
        ax = one_plot(ts)
        filepath = make_png_filename(vn, folder)
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(filepath)   # <----------
        plt.close()
        # except Exception as e:
#    raise Exception("Error plotting variable: " + str(vn))


# ############### #
# TO_PNG BLOCK 3: #
# ############### #


DEFAULT_START_YEAR = 2011
DIRS = {".png": "png", ".xls": "xls"}
MY_DPI = 96
GRAPH_WIDTH_HEIGHT_PX = (600, 450)


class Indicators():

    def __init__(self, groupname, labels, freq=None, start=None, end=None,
                 default_start_year=DEFAULT_START_YEAR):

        self.basename = groupname

        if not start:
            start = str(default_start_year) + "-01"

        self.dfa = self.make_df(labels, "a", start, end)
        self.dfq = self.make_df(labels, "q", start, end)
        self.dfm = self.make_df(labels, "m", start, end)

        if not freq:
            self.df = self.dfm
        elif freq in "aqm":
            self.freq = freq
            self.df = {"a": self.dfa, "q": self.dfq, "m": self.dfm}[freq]
        else:
            raise Exception("Wrong frequency: " + str(freq))

    def make_df(self, labels, freq, start, end,
                dfs={'a': DFA, 'q': DFQ, 'm': DFM}):
        df = dfs[freq]
        filtered_labels = [x for x in labels if x in df.columns]
        df = df[filtered_labels].loc[start:end, :]
        if df.empty:
            df["None"] = 0
            print("Warning: missing data in", ",".join(labels))
        return df

        # here
    def to_png(self, my_dpi=MY_DPI, dirs=DIRS, pix=GRAPH_WIDTH_HEIGHT_PX):
        ext = ".png"
        path = os.path.join(dirs[ext], self.freq + "_" + self.basename + ext)
        if not self.df.empty:
            ax = self.df.plot(figsize=(pix[0] / my_dpi, pix[1] / my_dpi))
            fig = ax.get_figure()
            fig.savefig(path, dpi=MY_DPI)  # <----------------
            fig.clear()
        return "<img src=\"{0}\">".format(path)

# saves indicators
#    def to_excel(self, dirs = DIRS):
#        ext = ".xls"
#        path = os.path.join(dirs[ext], self.basename + ext)
#        with pd.ExcelWriter(path) as writer:
#           self.dfa.to_excel(writer, sheet_name='Annual')
#           self.dfq.to_excel(writer, sheet_name='Quarterly')
#           self.dfm.to_excel(writer, sheet_name='Monthly')
#        # todo: clean first column in xls file
#        return "<a href=\"{0}\">{1}</a>".format(path, self.basename + ext)
