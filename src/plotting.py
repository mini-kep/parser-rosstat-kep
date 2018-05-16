# plotting

import matplotlib.pyplot as plt

from access import dfa, dfq, dfm 


start_year = 2016

renamer = {'INDPRO_yoy': ('Промышленное производство', 'темп прироста за 12 мес., %'),
           'GDP_yoy': ('Валовый внутренний продукт', 'темп прироста за 12 мес., %'),
           'RETAIL_SALES_yoy': ('Розничные продажи', 'темп прироста за 12 мес., %'),
           'CPI_rog': ('Индекс потребительских цен', 'к пред.периоду, %'),
           'WAGE_REAL_rog':('Реальная заработная плата', 'к пред.периоду, %'),
           'AGROPROD_yoy':('Сельскохозяйственное производство', 'темп прироста за 12 мес., %')
           }


fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(4*3.5, 3*3.5))    


a = dict(subplot_location=(0,0), freq='m', name='INDPRO_yoy') 
b = dict(subplot_location=(1,0), freq='m', name='CPI_rog') 
c = dict(subplot_location=(1,1), freq='m', name='RETAIL_SALES_yoy') 
d = dict(subplot_location=(0,1), freq='m', name='AGROPROD_yoy')

def plot_one(subplot_location, freq, name):
    ts = dfm[name]
    ix = ts.index.year >= start_year
    ts = ts[ix] - 100
    latest_value = round(ts[-1],2)
    latest_date = ts.index[-1].strftime('%Y-%m') 
    title = f'{renamer.get(name)[0]}\n{renamer.get(name)[1]}'
    rtitle = f'{latest_date}: {latest_value}'    
    
    
    ax = ts.plot(ax=axes[subplot_location], 
            color='lightblue',         
            lw = 3) 
    ax.set_title(title, loc='left')
    ax.set_title(rtitle, loc='right')
    ax.axhline(y=0, color='black', ls='dotted', lw = 0.5) 

plot_one(**a)
plot_one(**b)
plot_one(**c)
plot_one(**d)
plt.tight_layout()

#ax.set_xticklabels(ts.index.map(lambda t: t.strftime('%Y')))
# see plotting  at       
# splines?
# https://github.com/mini-kep/parser-rosstat-kep/blob/2743e624f39246e9760e733ab67ee281fc657cf9/notebooks/images.py
# see https://github.com/epogrebnyak/plotting/blob/master/matlibplot-ref/4graph.py

