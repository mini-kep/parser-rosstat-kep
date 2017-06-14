"""
ID  | Название  | Ед.изм.  | Последнее значение  |  Sparkline
--- | --------- | -------- | ------------------- | --------------------
CPI | Индекс потребительских цен | изменение к предыдущему месяцу | 1.015 (02.2017) |![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Sparkline_dowjones_new.svg/189px-Sparkline_dowjones_new.svg.png)


-------------------------------------------------------------------------------
Снятие сезонности 
- К

-------------------------------------------------------------------------------
Название и единицы измерения
- описание по названию переменной
- размерность переменной 
- частоты значений AQM

-------------------------------------------------------------------------------
Разделы - секции:
- восстановить логику поиска переменных по разделам
- статистика сколько переменных считано
- генерировать frontage по разделам

-------------------------------------------------------------------------------
Структура файлов:
- где будет frontpage.md
- где будет frontpage.py
- структура каталогов с картинками

-------------------------------------------------------------------------------
Больше страниц:
- проваливаться при нажатии
- страница индивидуального показателя
- как выбирать годовой, месячный и квартальный? названия

-------------------------------------------------------------------------------
Вне этого файла:
- переименовать классы Dataframes
- нужно ли нам генериовать pdf?
- исходный рисунок, не проще ли с seaborn?

-------------------------------------------------------------------------------
Рисунки:
- нужно ли нам генериовать pdf?
- исходный рисунок, не проще ли с seaborn?

-------------------------------------------------------------------------------
Отрисовка спарклайна:
- белый фон
- одинаковая шкала
- крупная последняя точка
- разные цвета линии и точки

-------------------------------------------------------------------------------
Подумать:
- такая же страница по квартальным данным
- такая же страница по годовым данным
- что реалицуем в md этом репозитарии, а что в html-view?
- популярность показателя
- валютные курсы в разных разрезах
-------------------------------------------------------------------------------
"""

import os
import matplotlib.pyplot as plt


from kep import KEP
import kep.config as config
from tabulate import pure_tabulate


#-------------------------------------------------------------------------------
#
# Plotting
#
#-------------------------------------------------------------------------------


def spark(data):    
    fig = plt.figure(figsize=(2, 0.5))
    ax = fig.add_subplot(111)
    ax.plot(data)
    for k,v in ax.spines.items():
        v.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    #plt.plot(len(data) - 1, data[len(data) - 1], 'r.')
    #ax.fill_between(range(len(data)), data, len(data)*[min(data)], alpha=0.1)
    
    return ax 

#-------------------------------------------------------------------------------
#
# Saving png
#
#-------------------------------------------------------------------------------

def make_png_filename(vn, dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return os.path.join(dirpath, "%s_spark.png" % vn)


def spark_png_fn(varname):
    return "%s_spark.png" % varname


def write_sparkline_pngs(df, folder = config.PNG_FOLDER):
    for vn in df.columns:
       ts = df[vn]
       # one_plot returns Axes and sets matplotlib's current figure to the plot 
       # it draws        
       ax = spark(ts)
       filepath = os.path.join(folder, spark_png_fn(vn))
       plt.subplots_adjust(bottom=0.15)
       plt.savefig(filepath)
       plt.close()

#-------------------------------------------------------------------------------
#
# Making markdown
#
#-------------------------------------------------------------------------------

def stream_table_rows():
    dfm = KEP().dfm.drop(['year', 'month'], 1)
    for name in dfm.columns:
       value, date = get_last(dfm, name) 
       img = insert_image_to_md(name)
       yield name, value, date, img

def get_last(df, lab):
    s = df[lab]
    ix = ~s.isnull()
    last_value = s[ix][-1]
    last_date = s.index[ix][-1]
    return str(round(last_value,2)), last_date.strftime("%m.%Y")

def insert_image_to_md(varname):
    folder = "https://github.com/epogrebnyak/data-rosstat-kep/raw/master/output/png/"
    path = folder + spark_png_fn(varname)
    return '![](%s)' % path
  
def get_md_code():
    header = ["Код", "Значение", "Дата", ""]
    rows = list(stream_table_rows())
    return pure_tabulate(rows, header)

def generate_md(md_file):
    md_code = get_md_code()
    with open(md_file, 'w', encoding = 'utf-8') as f:
        f.writelines(md_code)            
    
if __name__ == "__main__":
    dfm = KEP().dfm.drop(['year', 'month'], 1)    
    lab = 'RUR_EUR_eop'
    assert len(get_last(dfm, lab)) == 2
    
    s = dfm[lab]
    spark(s) 
    #write_sparkline_pngs(dfm)

    generate_md("frontpage.md")