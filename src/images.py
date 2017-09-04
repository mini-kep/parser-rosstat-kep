# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt

from config import find_repo_root

import getter


#Псеводкод использования:
# выбрать конкретный показатель 
# ts = dfm.RETAIL_SALES_FOOD_bln_rub
# создать инстанс графика
# spline1 = Spline(ts)
# нарисовать граифк в консоли
# spline1.show()
# сохранить в дефолтное для этого типа графоков место в файлоой системе
# spline1.save()
# сохранить в названный каталог (для тестирвоания)
# spline1.save(folder)


# Этот код должен быть в __main__ для отладки для
# Spline
# IndicatorChart

DEFAULT_TIMERANGE = datetime.date(1998, 12, 31), datetime.date(2017, 12, 31)

DEFAULT_GPARAMS = {'timerange':DEFAULT_TIMERANGE, 
                        'figsize':(10, 10), 'style':'ggplot', 'facecolor':'white',
                        'auto_x':False, 'axis_on':True}

SPLINE_GPARAMS = {'timerange':DEFAULT_TIMERANGE, 
                        'figsize':(2, 0.6), 'style':'ggplot', 'facecolor':'white',
                        'auto_x':False, 'axis_on':False}

INDICATOR_GPARAMS = {'timerange':DEFAULT_TIMERANGE, 
                        'figsize':(5, 5), 'style':'bmh', 'facecolor':'white',
                        'auto_x':True, 'axis_on':True}


class GraphBase:
    #TODO: need real short docstring what this class is.
    def __init__(self, tss, params=DEFAULT_GPARAMS, fname='untitled'):
        """
        Args:
            tss: list of timeseries to plot.
                for a simple chart len(tss) = 1
            params: chart formatting/style parameters      
        """
        self.tss = tss
        self.params = params
        self.fig = None
        
        self.rootfolder = find_repo_root()
        self.pngfolder = self.rootfolder / 'output' / 'png'
        self.subfolder = 'misc'     # will be overridden by child classes
        self.fname = fname

    def __del__(self):
        # plt.close()
        pass

    def plot(self):
        """
        What does this function do?
        Is there special kind of formatting applied to all graphs?
        
        Returns:
            None          
        """
        plt.style.use(self.params['style'])
        fig = plt.figure(figsize=self.params['figsize'])
        axes = fig.add_subplot(1, 1, 1, facecolor=self.params['facecolor'])
        for ts in self.tss:
            axes.plot(ts)
        axes.set_xlim(self.params['timerange'])
        if self.params['auto_x']:
            fig.autofmt_xdate()
        if not self.params['axis_on']:
            plt.axis('off')
        
        self.fig = fig

    def save(self):
        if self.fig == None:
            raise ValueError('Figure is empty, call GraphBase.plot() first')
        else:
            self.fig.savefig(self.get_fpath())
            
    def close(self):
        plt.close()
        del self.fig
        self.fig = None

    def get_fpath(self):
        fpath = str(self.pngfolder / self.subfolder / (self.fname+'.png'))
        return fpath


class Spline(GraphBase):
    def __init__(self, tss, fname):
        assert len(tss) == 1
        super().__init__(tss, params=SPLINE_GPARAMS, fname=fname)
        self.subfolder = 'splines'


class IndicatorChart(GraphBase):
    def __init__(self, tss, fname):
        assert len(tss) > 0
        super().__init__(tss, params=INDICATOR_GPARAMS, fname=fname)
        if len(tss) > 1:
            self.subfolder = 'mul_indicators'
        else:
            self.subfolder = 'indicators'        





def plot_all_images(save=True):
    dfs = {key:getter.get_dataframe(key) for key in 'aqm'}

    df = dfs['m']
    cols = df.columns
    cols = cols.drop(['year', 'month'])       

    graphs = []

# type 1 and 2 graphs
    for col in cols:
        ts = df[col]
        graphs.append(Spline        ([ts], col))
        graphs.append(IndicatorChart([ts], col))

# type 3 graphs
    inds = ['RETAIL_SALES_FOOD_bln_rub', 
            'RETAIL_SALES_NONFOOD_bln_rub']
    tss = [df[col] for col in inds]
    name = '_AND_'.join(sorted(inds))
    graphs.append(IndicatorChart(tss, name))
    
# plotting and saving all
    for graph in graphs:
        graph.plot()
        graph.save()
        graph.close()



    
# TODO: EP - add tasks.py command/integrate to finaliser.py for latest graphs.   
    
if __name__ == "__main__":
    plot_all_images()    
    
 