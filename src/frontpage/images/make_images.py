# -*- coding: utf-8 -*-

from pathlib import Path

def get_root():
	return Path(__file__).parents[3]

import access_dfs

import matplotlib.pyplot as plt
plt.style.use('ggplot')

class Visualizer:
	def __init__(self):
		self.dfs = access_dfs.get_dfs_from_web()
		self.rootfolder = get_root()
		self.pngfolder = self.rootfolder / 'output' / 'png'

	def gen_splines(self):
		outpath = self.pngfolder / 'splines'

		cols = self.dfs['m'].columns
		cols = cols.drop(['year', 'month'])   

		fig = plt.figure(figsize=(2, 0.6))	
		for col in cols:
			ts = self.dfs['m'][col]

			axes = fig.add_subplot(1, 1, 1, facecolor='white')
			axes.plot(ts)
			plt.axis('off')

			name = "{}.png".format(col)
			plt.savefig(str(outpath / name))
			
			plt.cla()  # close axes


viz = Visualizer()
viz.gen_splines()