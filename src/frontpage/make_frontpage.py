from pathlib import Path
import sys
import matplotlib.pyplot as plt
import os

# add the 'kep_dir' directory as one where we can import modules
#    see 'Notebooks are for exploration and communication' in 
#    http://drivendata.github.io/cookiecutter-data-science/

kep_dir = Path(__file__).parents[1] / "kep" 
access_dir =  Path(__file__).parents[1] / "access_data"              
sys.path.extend([path.__str__() for path in [kep_dir, access_dir]])

import cfg
from to_markdown import to_markdown
from access_data import get_dfs

# TABLE 1 - Sections with required varnames
md1 = to_markdown(body=cfg.yield_variable_descriptions_with_subheaders(), 
                  header=["Показатель", "Код"])
path = Path(__file__).parent / "sections.md"
path.write_text(md1)  
print(md1)


# TABLE 2 - latest values for all monthly variables
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py#L120-L153
# or local old/frontpage.py#L120-L153

dfa, dfq, dfm = get_dfs()

#generate with latest values from monthly dataframe
def stream_table_rows(dfm=dfm):
    dfm = dfm.drop(['year', 'month'], 1)
    for name in dfm.columns:
       value, date = get_last(dfm, name) 
       #FIXME: generate and add sparklines
       #img = insert_image_to_md(name)
       #FIXME: pad_cells(table) wont accept tuple, need make it more type-agnostc
       yield [name, value, date]#, img

def get_last(df, lab):
    s = df[lab]
    ix = ~s.isnull()
    last_value = s[ix][-1]
    last_date = s.index[ix][-1]
    return str(round(last_value,2)), last_date.strftime("%m.%Y")

md2 = to_markdown(body=stream_table_rows(), 
                  header=["Код", "Значение", "Дата"])
path = Path(__file__).parent / "latest.md"
path.write_text(md2)  
print(md2)


# TABLE 3
# TODO: generate TABLE 3 with a column of sparklines as in below 
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py
# or local old/frontpage.py

# всё ниже относится к TABLE 3 таску
FRONTPAGE_FOLDER, _ = os.path.split(__file__)
# пока временно так, предполагается что папка src/frontpage/pngs существует
PNG_FOLDER = os.path.join(FRONTPAGE_FOLDER, 'pngs')


def write_sparkline_pngs(df, folder=PNG_FOLDER):
    df = df.drop(['year', 'month'], 1)
    for vn in df.columns:
        ts = df[vn]
        # one_plot returns Axes and sets matplotlib's current figure to the plot
        # it draws
        ax = spark(ts)
        filepath = os.path.join(folder, spark_png_fn(vn))
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(filepath)
        plt.close()


def spark(data):
    fig = plt.figure(figsize=(2, 0.5))
    ax = fig.add_subplot(111)
    ax.plot(data, 'r-')
    for _, v in ax.spines.items():
        v.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # plt.plot(len(data) - 1, data[len(data) - 1], 'r.')
    # ax.fill_between(range(len(data)), data, len(data)*[min(data)], alpha=0.1)

    return ax


def spark_png_fn(varname):
    return "%s_spark.png" % varname


def insert_image_to_md(name, folder=PNG_FOLDER):
    path = folder + "/" + spark_png_fn(name)
    return '![](%s)' % path


def stream_table_rows_images(dfm=dfm):
    dfm = dfm.drop(['year', 'month'], 1)
    for name in dfm.columns:
        img = insert_image_to_md(name)
        yield [img]

# создаем сами файлы с изображениями
# если сами изображения не нужно хранить в репозитории, потребуется обновить соответственно .gitignore
write_sparkline_pngs(dfm)

# создаем таблицу из 1 колонки (заголовок: "", содержимое: пути до изображений, созданных выше в write_sparkline_pngs)
md3 = to_markdown(body=stream_table_rows_images(),
                  header=[""])

# пишем в файл "images_paths.md"
path = Path(__file__).parent / "images_paths.md"
path.write_text(md3)
print(md3)

# TABLE 4
# NOT TODO: mix table 1 and table 3
