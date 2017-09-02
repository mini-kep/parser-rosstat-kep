# -*- coding: utf-8 -*-

import sys

import datetime
from pathlib import Path

def get_root():
    return Path(__file__).parents[3]

sys.path.append(str(get_root() / 'src'))
import getter

import matplotlib.pyplot as plt

DEFAULT_TIMERANGE = datetime.date(1998, 12, 31), datetime.date(2017, 12, 31)

class GraphInstance:
    def __init__(self, tss, timerange=DEFAULT_TIMERANGE, 
                        figsize=(10,10), style='ggplot', facecolor='gray',
                        auto_x=False, axis_on=True):
        self.tss = tss
        self.timerange = timerange
        self.figsize = figsize
        self.style = style
        self.facecolor = facecolor
        self.auto_x = auto_x
        self.axis_on = axis_on

    def __del__(self):
        plt.close()

    def plot(self):
        plt.style.use(self.style)

        fig = plt.figure(figsize=self.figsize)

        axes = fig.add_subplot(1, 1, 1, facecolor=self.facecolor)
        for ts in self.tss:
            axes.plot(ts)
        axes.set_xlim(self.timerange)
        if self.auto_x:
            fig.autofmt_xdate()
        if not self.axis_on:
            plt.axis('off')

        return fig


class SplineInstance(GraphInstance):
    def __init__(self, tss):
        assert len(tss) == 1
        super().__init__(tss, timerange=DEFAULT_TIMERANGE, 
                        figsize=(2, 0.6), style='ggplot', facecolor='white', 
                        auto_x=False, axis_on=False)

    # def plot(self):
    #     return None


class IndicatorInstance(GraphInstance):
    def __init__(self, tss):
        super().__init__(tss, timerange=DEFAULT_TIMERANGE, 
                        figsize=(5, 5), style='bmh', facecolor='white', 
                        auto_x=True)

    # def plot(self):
    #     return None



class DataHandler:
    def __init__(self):
        self.dfs = getter.get_dfs_as_dictionary()
        self.rootfolder = get_root()
        self.pngfolder = self.rootfolder / 'output' / 'png'

    def gen_all_graphs(self, freq, gtype=GraphInstance):
        if gtype == SplineInstance:
            subp = 'splines'
        elif gtype == IndicatorInstance:
            subp = 'indicators'
        elif gtype == GraphInstance:
            subp = 'misc'
        else:
            raise TypeError(repr(gtype)+' is not a known graph type')

        outpath = self.pngfolder / subp

        cols = self.dfs[freq].columns
        cols = cols.drop(['year', 'month'])   
   
        for col in cols:
            ts = self.dfs[freq][col]
            ginstance = gtype([ts])
            name = "{}.png".format(col)
            fpath = str(outpath / name)
            ginstance.plot().savefig(fpath)
            del ginstance

    def gen_splines(self, freq='m'):
        self.gen_all_graphs(freq, gtype=SplineInstance)

    def gen_indicators(self, freq='m'):
        self.gen_all_graphs(freq, gtype=IndicatorInstance)

    def gen_multiple_indicators(self, inds, freq='m'):
        outpath = self.pngfolder / 'mul_indicators'

        tss = [self.dfs[freq][col] for col in inds]
        name = "{}.png".format('_AND_'.join(sorted(inds)))
        fpath = str(outpath / name)

        ginstance = IndicatorInstance(tss)
        ginstance.plot().savefig(fpath)
        del ginstance



def save_all_images():
    dh = DataHandler()
    dh.gen_splines('m')
    dh.gen_indicators('m')

    inds = ['RETAIL_SALES_FOOD_bln_rub', 
            'RETAIL_SALES_NONFOOD_bln_rub']
    dh.gen_multiple_indicators(inds, 'm')
