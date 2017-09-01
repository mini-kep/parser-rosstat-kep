# -*- coding: utf-8 -*-

import datetime
from pathlib import Path

def get_root():
    return Path(__file__).parents[3]

import access_dfs

import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self):
        self.dfs = access_dfs.get_dfs_from_web()
        self.rootfolder = get_root()
        self.pngfolder = self.rootfolder / 'output' / 'png'

    def gen_splines(self, freq='m'):
        outpath = self.pngfolder / 'splines'

        cols = self.dfs[freq].columns
        cols = cols.drop(['year', 'month'])   

        plt.style.use('ggplot')
        fig = plt.figure(figsize=(2, 0.6))    

        for col in cols:
            ts = self.dfs[freq][col]

            axes = fig.add_subplot(1, 1, 1, facecolor='white')
            axes.plot(ts)
            plt.axis('off')

            name = "{}.png".format(col)
            plt.savefig(str(outpath / name))
            
            plt.cla()  # close axes

    def gen_ts(self, fig, tss, timerange, fpath):
        axes = fig.add_subplot(1, 1, 1, facecolor='white')
        for ts in tss:
            axes.plot(ts)
        axes.set_xlim()
        fig.autofmt_xdate()
        plt.savefig(fpath)
        plt.cla()

    def gen_indicators(self, freq='m'):
        outpath = self.pngfolder / 'indicators'

        cols = self.dfs[freq].columns
        cols = cols.drop(['year', 'month'])   

        plt.style.use('bmh')
        fig = plt.figure(figsize=(5,5))

        for col in cols:
            ts = self.dfs[freq][col]
            fpath = str(outpath / "{}.png".format(col))

            self.gen_ts(fig, [ts], 
                        [datetime.date(1998, 12, 31), datetime.date(2017, 12, 31)],
                        fpath)
    
    def gen_multiple_indicators(self, inds, freq='m'):
        outpath = self.pngfolder / 'mul_indicators'

        plt.style.use('bmh')
        fig = plt.figure(figsize=(5,5))

        tss = [self.dfs[freq][col] for col in inds]

        name = "{}.png".format('_AND_'.join(sorted(inds)))
        fpath = str(outpath / name)

        self.gen_ts(fig, tss, 
                    [datetime.date(1998, 12, 31), datetime.date(2017, 12, 31)],
                    fpath)


viz = Visualizer()
viz.gen_splines('m')
viz.gen_indicators('m')

inds = ['RETAIL_SALES_FOOD_bln_rub', 
        'RETAIL_SALES_NONFOOD_bln_rub']
viz.gen_multiple_indicators(inds, 'm')
