# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt

from config import find_repo_root

import getter


# Псеводкод использования:
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

# QUESTION Вопрос - может ли это все тестироваться? Частично?

DEFAULT_TIMERANGE = datetime.date(1998, 12, 31), datetime.date(2017, 12, 31)


# TODO: allocate parameters between GraphBase and child classes

class GraphBase:
    # TODO: need real short docstring what this class is.
    def __init__(self, tss, timerange=DEFAULT_TIMERANGE,
                 figsize=(10, 10), style='ggplot', facecolor='gray',
                 auto_x=False, axis_on=True):
        """
        Args:
            WTF is tss? dataframe? time series?
        """
        # FIXME: это и так базовый класс, может не загонять через аргумент, а сразу присвоить
        #        лучше зесь оставить параметры, которые не меняются дочерним классом
        #        можно также словарем конфигурировать
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
        """
        What does this function do?
        Is there special kind of formatting applied to all graphs?

        Returns:
            what type?
        """
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


class Spline(GraphBase):
    def __init__(self, tss):
        assert len(tss) == 1
        # FIXME: надо как-то разоббраться с аргументами - какие не меняются
        #       и устанавливаются в GraphBase, а какие заадаются в завивмости от типа
        #
        super().__init__(tss, timerange=DEFAULT_TIMERANGE,
                         figsize=(2, 0.6), style='ggplot', facecolor='white',
                         auto_x=False, axis_on=False)


class IndicatorChart(GraphBase):
    def __init__(self, tss):
        super().__init__(tss, timerange=DEFAULT_TIMERANGE,
                         figsize=(5, 5), style='bmh', facecolor='white',
                         auto_x=True)

# NEED COMMENT: у нас был третий тип граификов c с группой показателей - он отрисовывается черз IndicatorGraph?
# или на него забили пока? в этом случае нужен пустой класс. или него
# забили? тоже нужен комментарий


# COMMENT все ниже видимо под нож, к сожалениюю
# часть с файловыми именами должна быть переложена в соотв
# отдельно - скрыйтый метод для создания имени, отдельно метод для
# создания пути файла

# жалко что все пошло не по пути который мы одсуждали - dataHndler есть, но он пытается
# разобраться в типах данных и большой (если честно - жесть;), а не
# маленький для каждого.

# функция типа plot_all() должна создавать серию инстансов и применять
# метод save кним.

class DataHandler:
    def __init__(self):
        #
        self.dfs = {key: getter.get_dataframe(key) for key in 'aqm'}
        self.rootfolder = find_repo_root()
        self.pngfolder = self.rootfolder / 'output' / 'png'

    def gen_all_graphs(self, freq, gtype=GraphBase):
        if gtype == Spline:
            subp = 'splines'
        elif gtype == IndicatorChart:
            subp = 'indicators'
        elif gtype == GraphBase:
            subp = 'misc'
        else:
            raise TypeError(repr(gtype) + ' is not a known graph type')

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
        self.gen_all_graphs(freq, gtype=Spline)

    def gen_indicators(self, freq='m'):
        self.gen_all_graphs(freq, gtype=IndicatorChart)

    def gen_multiple_indicators(self, inds, freq='m'):
        outpath = self.pngfolder / 'mul_indicators'

        tss = [self.dfs[freq][col] for col in inds]
        name = "{}.png".format('_AND_'.join(sorted(inds)))
        fpath = str(outpath / name)

        ginstance = IndicatorChart(tss)
        ginstance.plot().savefig(fpath)
        del ginstance


def save_all_images():
    dh = DataHandler()
    dh.gen_splines('m')
    dh.gen_indicators('m')

    # видимо это и есть третий тип индикаторов, нужнов Indiciator
    # отметиьт что аргумент может быть dataframe'ом
    inds = ['RETAIL_SALES_FOOD_bln_rub',
            'RETAIL_SALES_NONFOOD_bln_rub']
    dh.gen_multiple_indicators(inds, 'm')


# TODO: EP - add tasks.py command/integrate to finaliser.py for latest graphs.

if __name__ == "__main__":
    save_all_images()
