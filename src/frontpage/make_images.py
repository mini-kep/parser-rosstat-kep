# -*- coding: utf-8 -*-
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import os


# see 'Notebooks are for exploration and communication' in
# http://drivendata.github.io/cookiecutter-data-science/
def get_root():
    return Path(__file__).parents[2]


src_root = Path(__file__).parents[1]
sys.path.extend(str(src_root / "csv2df"))
sys.path.extend(str(src_root / "access_data"))

files_dir = Path(__file__).parent
sections_file = files_dir / "_sections.md"
latest_values_file = files_dir / "_latest.md"
monthy_images = files_dir / "_images_paths.md"

# import cfg
from to_markdown import to_markdown
import example_access_data as access_data

# TABLE 1 - Sections with required varnames
# FIXME: cfg.yield_variable_descriptions_with_subheaders


def bold(s):
    return"**{}**".format(s)


# def yield_variable_descriptions_with_subheaders(sections=cfg.SECTIONS,
#                                                 desc=cfg.DESC):

#     for section_name, labels in sections.items():
#         yield([bold(section_name), ""])
#         for label in labels:
#             yield([desc[label], label])


# md1 = to_markdown(body=yield_variable_descriptions_with_subheaders(),
#                   header=["Показатель", "Код"])
# sections_file.write_text(md1)
# print(md1)

# TABLE 2 - latest values for all monthly variables
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py#L120-L153
# or local old/frontpage.py#L120-L153

dfa, dfq, dfm = access_data.get_dfs_from_web()

# generate with latest values from monthly dataframe


def stream_table_rows(dfm=dfm):
    dfm = dfm.drop(['year', 'month'], 1)
    for name in dfm.columns:
        value, date = get_last(dfm, name)
        # FIXME: generate and add sparklines
        #img = insert_image_to_md(name)
        # FIXME: pad_cells(table) wont accept tuple, need make it more
        # type-agnostc
        yield [name, value, date]  # , img


def get_last(df, lab):
    s = df[lab]
    ix = ~s.isnull()
    last_value = s[ix][-1]
    last_date = s.index[ix][-1]
    return str(round(last_value, 2)), last_date.strftime("%m.%Y")


md2 = to_markdown(body=stream_table_rows(),
                  header=["Код", "Значение", "Дата"])
latest_values_file.write_text(md2)
#*print(md2)


# TABLE 3
# TODO: generate TABLE 3 with a column of sparklines as in below
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py
# or local old/frontpage.py

# всё ниже относится к TABLE 3 таску






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
        plt.savefig(self.path())         #  <----------------
        plt.close()

    def markdown(self):
        path = self.GITHUB_FOLDER.format(self.filename())
        return '![]{}'.format(path)


def make_sparks(df, save=False):
    df = df.drop(['year', 'month'], 1)
    for vn in df.columns:
        ts = df[vn]
        Sparkline(ts).save()


# TODO: make quarterly spark pngs

if __name__ == "__main__":
    make_sparks(dfm)
    # print(md1)
    # print(md2)
    # print(md3)
    pass


# ############### #
# TO_PNG BLOCK 2: #
# ############### #

from matplotlib.ticker import NullFormatter
from pandas.tseries.converter import TimeSeries_DateFormatter


matplotlib.style.use('ggplot')

# The default figsize is the size of an A4 sheet in inches
A4_SIZE_PORTRAIT = [8.27, 11.7]
TITLE_FONT_SIZE = 12


def one_plot(df, nrows=3, ncols=2, figsize=A4_SIZE_PORTRAIT, title_font_size=TITLE_FONT_SIZE):
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

#here
def write_png_pictures(df, folder):
    for vn in df.columns:
        # Indexing df as df[[vn]] produces a DataFrame, not a Series. Therefore,
        # it does not have a .name attribute, but it has .columns instead.
            ts = df[vn]

        # one_plot returns Axes and sets matplotlib's current figure to the plot it draws
        #try:
            ax = one_plot(ts)
            filepath = make_png_filename(vn, folder)
            plt.subplots_adjust(bottom=0.15)
            plt.savefig(filepath)   # <----------
            plt.close()
        #except Exception as e:
#    raise Exception("Error plotting variable: " + str(vn))




# ############### #
# TO_PNG BLOCK 3: #
# ############### #


DEFAULT_START_YEAR = 2011
DIRS = {".png":"png", ".xls":"xls"}
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
           self.df  = {"a":self.dfa,"q":self.dfq,"m":self.dfm}[freq]  
        else:
           raise Exception("Wrong frequency: " + str(freq)) 
      
    def make_df(self, labels, freq, start, end,  
                dfs={'a': DFA, 'q': DFQ, 'm': DFM}):
        df = dfs[freq]        
        filtered_labels = [x for x in labels if x in df.columns] 
        df = df[filtered_labels].loc[start:end,:]
        if df.empty:
            df["None"]=0
            print("Warning: missing data in", ",".join(labels))
        return df

	# here         
    def to_png(self, my_dpi = MY_DPI, dirs = DIRS, pix = GRAPH_WIDTH_HEIGHT_PX):    
        ext = ".png"
        path = os.path.join(dirs[ext], self.freq + "_" + self.basename + ext)
        if not self.df.empty:
            ax = self.df.plot(figsize=(pix[0]/my_dpi, pix[1]/my_dpi))
            fig = ax.get_figure()
            fig.savefig(path, dpi = MY_DPI)  # <----------------
            fig.clear()
        return "<img src=\"{0}\">".format(path)      
        
        
    def to_excel(self, dirs = DIRS):        
        ext = ".xls"
        path = os.path.join(dirs[ext], self.basename + ext) 
        with pd.ExcelWriter(path) as writer:
           self.dfa.to_excel(writer, sheet_name='Annual')
           self.dfq.to_excel(writer, sheet_name='Quarterly')
           self.dfm.to_excel(writer, sheet_name='Monthly') 
        # todo: clean first column in xls file  
        return "<a href=\"{0}\">{1}</a>".format(path, self.basename + ext)                         
      
    def dump(self):
        self.to_png()
self.to_excel()


