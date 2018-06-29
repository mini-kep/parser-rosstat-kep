import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as dates

matplotlib.use('agg') # FIXME: is this necessary?
matplotlib.style.use('ggplot')

# WARNING:
#C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/notebook/write_pdf/create_png.py:2: UserWarning: 
#This call to matplotlib.use() has no effect because the backend has already
#been chosen; matplotlib.use() must be called *before* pylab, matplotlib.pyplot,
#or matplotlib.backends is imported for the first time.

def plot(df, title: str, minor_ticks, major_ticks):
    """Plot dataframe with title and ticks specification."""
    ax = df.plot(x_compat=True)           
    # set ticks
    ax.set_xticks(minor_ticks, minor=True)
    ax.xaxis.set_ticks(major_ticks, minor=False)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate(rotation=0, ha="center") 
    # other formatting
    plt.legend(loc="lower left")
    ax.set_title(title, loc='left', fontdict = {'fontsize': 11})
    return ax    

    
def plot_long(df, title, start=2005, end=2020, left_offset=1):
    """Plot starting 2005."""
    df = df[df.index>=str(start)]
    minor_ticks = pd.date_range(str(start-left_offset), str(end), freq='YS')
    major_ticks = pd.date_range(str(start), str(end), freq='5YS') 
    return plot(df, title, minor_ticks, major_ticks)

def save(filename):
    plt.savefig(filename)
    
    
if __name__ == '_main__':
    import access   
    dfa, dfq, dfm = (access.get_dataframe(freq) for freq in 'aqm')
    df = dfm.DWELLINGS_CONSTRUCTION_mln_m2
    ax = plot_long(df, 'Ввод жилья, млн.кв.м')
    plt.show()
    
    
