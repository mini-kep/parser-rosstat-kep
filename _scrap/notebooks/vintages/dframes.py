# -*- coding: utf-8 -*-
"""Operate with dataframes based on 'processed' data."""

from pathlib import Path
import pandas as pd

# we are in <root>/analysis/vintages
levels_up = 2
processed = Path(__file__).parents[levels_up] / 'data' / 'processed'


def filled_dates_local(root=processed):
    def listing(folder):
        gen = [f.name for f in folder.iterdir() if f.is_dir()]
        return reversed(sorted(gen))
    for subfolder in listing(root):
        for s in listing(root / subfolder):
            yield (int(subfolder), int(s))


def get_processed_folder(year, month, root=processed):
    month_dir = str(month).zfill(2)
    return root / str(year) / month_dir


def from_csv(filename):
    df = pd.read_csv(filename, index_col=0)
    df.index = pd.to_datetime(df.index)
    return df


def get_dataframes(year, month):
    folder = get_processed_folder(year, month)
    dfa = pd.read_csv(folder / "dfa.csv", index_col=0)
    dfq = from_csv(folder / "dfq.csv")
    dfm = from_csv(folder / "dfm.csv")
    return dfa, dfq, dfm


def get_vintages(label):
    for date in filled_dates_local():
        _, dfq, _ = get_dataframes(*date)
        ts = dfq.loc[:, label]
        year, month = date
        ts.name = str(year) + "_" + str(month)
        yield ts


vints = list(get_vintages('GDP__yoy'))
df = pd.concat(vints, axis=1)
print(df.transpose())
# FIXME: write file elsewhere
df.transpose().to_excel("gdp.xls")

# FIXME: produce plots
#    def write_monthly_pdf(self):
#        df = self.dfm.drop(['year', 'month'], 1)
#        plots.save_plots_as_pdf(df, config.PDF_FILE)
#
#    def write_monthly_png(self):
#        df = self.dfm.drop(['year', 'month'], 1)
#        plots.write_png_pictures(df, config.PNG_FOLDER)
#        plots.generate_md(df, config.MD_FILE)
