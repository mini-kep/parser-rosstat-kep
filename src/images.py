# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt

from config import find_repo_root

def get_pix_folder(subfolder):    
    return find_repo_root() / 'output' / 'png' / subfolder


start = datetime.date(1998, 12, 31)
end = datetime.date(2017, 12, 31)
DEFAULT_TIMERANGE = start, end

# graphics parameters in dicts

SPLINE_GPARAMS = {'timerange':DEFAULT_TIMERANGE, 
                        'figsize':(2, 0.6), 'style':'ggplot', 'facecolor':'white',
                        'auto_x':False, 'axis_on':False}

INDICATOR_GPARAMS = {'timerange':DEFAULT_TIMERANGE, 
                        'figsize':(5, 5), 'style':'bmh', 'facecolor':'white',
                        'auto_x':True, 'axis_on':True}


class GraphBase:
    """Parent class for standard project charts.     
    
       Parent to:
            Spline
            IndicatorChart    
    """ 
    def __init__(self, ts, params):
        """
        Args:
            ts (pd.TimeSeries): 
            params: chart formatting/style parameters      
        """
        self.ts = ts
        self.params = params
        self.fig = None
        self.subfolder = None       

    def _get_filename(self):
        # FIXME will need to put frequency in, not todo now
        return f'{self.ts.name}.png'
        
    def _get_path(self):        
        return str(get_pix_folder(self.subfolder) / self._get_filename(self))
            
    def plot(self):
        #FIXME: желательно разделить на подгтовку осей / отрисовку / выдачу фигуры
        plt.style.use(self.params['style'])
        fig = plt.figure(figsize=self.params['figsize'])
        axes = fig.add_subplot(1, 1, 1, facecolor=self.params['facecolor'])
        # собственно plot, его желталеьно выделить чтобы перезагрузить в BranchChart
        axes.plot(ts)
        # ----
        axes.set_xlim(self.params['timerange'])
        if self.params['auto_x']:
            fig.autofmt_xdate()
        if not self.params['axis_on']:
            plt.axis('off')        
        self.fig = fig

    def save(self):
        if self.fig is None:
            raise ValueError('Figure is empty, call GraphBase.plot() first')
        else:
            self.fig.savefig(self.get_file_path())
            
    def close(self):
        plt.close()
        del self.fig
        self.fig = None


class Spline(GraphBase):
    def __init__(self, ts, name=None):
        super().__init__(ts, params=SPLINE_GPARAMS)
        self.subfolder = 'splines'


class IndicatorChart(GraphBase):
    def __init__(self, df, name=None):
        super().__init__(df, params=INDICATOR_GPARAMS)
        self.subfolder = 'indicators'        


class BranchChart(GraphBase):
    def __init__(self, df, name=None):
        super().__init__(df, params=INDICATOR_GPARAMS)
        self.subfolder = 'indicators'   
        
    # TODO: overload drawing method    

    # TODO: overload naming method  

def plot_all_images(save=True):
    dfa, dfq, dfm = [getter.get_dataframe(freq) for freq in 'aqm']

    df = dfm
    cols = df.columns
    cols = cols.drop(['year', 'month'])       

    graphs = []

    # type 1 and 2 graphs
    for col in cols:
        ts = df[col]
        graphs.append(Spline        ([ts], col))
        graphs.append(IndicatorChart([ts], col))

   
    # plotting and saving all
    for graph in graphs:
        graph.plot()
        graph.save()
        graph.close()


# Checklist

# SK:
# ключевое:    
# - [ ] разделили GraphBase.plot() 
# дополниельно:    
# - [ ] сделали класс BranchChart
# - [ ] assert/тесты для публичных классов

# EP:
# - [ ] ввели новый нейминг для картинок с разной частотой типа mCPI_rog.png
# - [ ] создаем очередь что рисовать 
# - [ ] запускаем очередь что рисовать 
# - [ ] tasks.py command/integrate to finaliser.py for latest graphs 


# Checklist 2
# - [ ] убрали name из инита + добавили set_name()  

if __name__ == "__main__":
    
    import getter
    dfa, dfq, dfm = (getter.get_dataframe(freq) for freq in 'aqm')
    
    ts = dfm.CPI_rog
    s = Spline(ts, 'name')
    ic = IndicatorChart(ts, 'name2')
    
    s.plot()
    ic.plot()
    
    
    # type 3 graphs
    varnames = ['RETAIL_SALES_FOOD_bln_rub', 
                'RETAIL_SALES_NONFOOD_bln_rub']
    df = dfm[varnames]
    bc = BranchChart(df)
