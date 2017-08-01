# -*- coding: utf-8 -*-
from pathlib import Path
import sys
import matplotlib.pyplot as plt


# see 'Notebooks are for exploration and communication' in
# http://drivendata.github.io/cookiecutter-data-science/
def get_root():
    return Path(__file__).parents[2]


src_root = Path(__file__).parents[1]
sys.path.extend(str(src_root / "kep"))
sys.path.extend(str(src_root / "access_data"))

files_dir = Path(__file__).parent
sections_file = files_dir / "_sections.md"
latest_values_file = files_dir / "_latest.md"
monthy_images = files_dir / "_images_paths.md"

import cfg
from to_markdown import to_markdown
import access_data

# TABLE 1 - Sections with required varnames
# FIXME: cfg.yield_variable_descriptions_with_subheaders


def bold(s):
    return"**{}**".format(s)


def yield_variable_descriptions_with_subheaders(sections=cfg.SECTIONS,
                                                desc=cfg.DESC):

    for section_name, labels in sections.items():
        yield([bold(section_name), ""])
        for label in labels:
            yield([desc[label], label])


md1 = to_markdown(body=yield_variable_descriptions_with_subheaders(),
                  header=["Показатель", "Код"])
sections_file.write_text(md1)
# print(md1)

# TABLE 2 - latest values for all monthly variables
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py#L120-L153
# or local old/frontpage.py#L120-L153

dfa, dfq, dfm = access_data.get_dfs()

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

class Sparkline():

    def __init__(self, ts):
        self.ts = ts

    def path(self):
        return Namer(self.ts.name).path()

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

    def save(self):
        self.plot()
        plt.subplots_adjust(bottom=0.15)
        plt.savefig(self.path())
        plt.close()


class Namer():

    LOCAL_FOLDER = get_root() / "output" / "png"
    GITHUB_FOLDER = \
        "https://github.com/epogrebnyak/mini-kep/raw/master/output/png/{}"

    def __init__(self, label):
        self.label = label

    def path(self):
        return str(self.LOCAL_FOLDER / self.filename())

    def filename(self):
        return "{}_spark.png".format(self.label)

    def markdown(self):
        path = self.GITHUB_FOLDER.format(self.filename())
        return '![]({})'.format(path)


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
