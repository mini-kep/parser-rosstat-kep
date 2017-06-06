# -*- coding: utf-8 -*-
from pathlib import Path
from collections import OrderedDict as odict   

# TODO: non-csv output directory locations

# csv file parameters
ENC = 'utf8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')

#FIXME: hardcoded constant will not update to new months
DATES =     [                                 (2009, 4), (2009, 5), (2009, 6), 
             (2009, 7), (2009, 8), (2009, 9), (2009, 10), (2009, 11), (2009, 12), 
             
             (2010, 1), (2010, 2), (2010, 3), (2010, 4), (2010, 5), (2010, 6), 
             (2010, 7), (2010, 8), (2010, 9), (2010, 10), (2010, 11), (2010, 12),
             
             (2011, 1), (2011, 2), (2011, 3), (2011, 4), (2011, 5), (2011, 6),
             (2011, 7), (2011, 8), (2011, 9), (2011, 10), (2011, 11), (2011, 12), 
             
             (2012, 1), (2012, 2), (2012, 3), (2012, 4), (2012, 5), (2012, 6), 
             (2012, 7), (2012, 8), (2012, 9), (2012, 10), (2012, 11), (2012, 12), 
             
             (2013, 1), (2013, 2), (2013, 3), (2013, 4), (2013, 5), (2013, 6), 
             (2013, 7), (2013, 8), (2013, 9), (2013, 10), # missing (2013, 11)
             (2013, 12), 
             
             (2014, 1), (2014, 2), (2014, 3), (2014, 4), (2014, 5), (2014, 6), 
             (2014, 7), (2014, 8), (2014, 9), (2014, 10), (2014, 11), (2014, 12), 
             
             (2015, 1), (2015, 2), (2015, 3), (2015, 4), (2015, 5), (2015, 6), 
             (2015, 7), (2015, 8), (2015, 9), (2015, 10), (2015, 11), (2015, 12), 
             
             (2016, 1), (2016, 2), (2016, 3), (2016, 4), (2016, 5), (2016, 6), 
             (2016, 7), (2016, 8), (2016, 9), (2016, 10), (2016, 11), (2016, 12), 
             
             (2017, 1), (2017, 2), (2017, 3), (2017, 4)]

# folder structure
"""
\data
  (\raw      
      \word)
  \interim
      \2017          
  \processed
      \latest_nsa
      \latest_sa
      \vintages
      \2017
      \...
"""
# we are in src/kep
levels_up = 2
data_folder = Path(__file__).parents[levels_up] / 'data' 
rosstat_folder = data_folder / 'interim'
processed = data_folder / 'processed'


def init_dirs(root, available_dates=DATES):
    for d in available_dates:
        y, m = d
        f = root / str(y)
        sf = f / str(m).zfill(2) 
        for new_folder in [f, sf]:
            if not new_folder.exists():
               new_folder.mkdir() 


class InterimDataLocation():
    """Find latest month available in interim data folder"""
    
    def __init__(self, folder=rosstat_folder):
        self.folder = folder
        self.dirs = self.listing(folder)

    def listing(self, _folder):
        return [f.name for f in _folder.iterdir() if f.is_dir()]
    
    def max_year(self):
        return max(self.dirs)
        
    def max_month(self):
        subfolder = self.folder / self.max_year()
        return max(self.listing(subfolder))
    
    def get_latest(self):
        return int(self.max_year()), int(self.max_month())


assert InterimDataLocation().get_latest() == DATES[-1]


def loc(year, month, root):
    if not year and not month:
        year, month = InterimDataLocation().get_latest()    
    if year and month:
        month_dir = str(month).zfill(2)
        return root / str(year) / month_dir 


def get_path_csv(year=None, month=None):
    """Return interim CSV file path based on year and month"""
    return loc(year, month, root=rosstat_folder) / 'tab.csv'


def get_processed_folder(year=None, month=None):  
    """Return processed CSV file path based on year and month"""
    return loc(year, month, root=processed)


# parsing specification
units = odict([('млрд.долларов', 'bln_usd'),
         ('млрд. долларов', 'bln_usd'),
         ('млрд, долларов', 'bln_usd'),
         ('млрд.рублей', 'bln_rub'),
         ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
         ('в % к ВВП', 'gdp_percent'),
         ('в % к декабрю предыдущего года', 'ytd'),
         ('в % к предыдущему месяцу', 'rog'),
         ('в % к предыдущему периоду', 'rog'),
         # this...
         ('период с начала отчетного года в % к соответствующему периоду предыдущего года', 'ytd'),
         # ... must preceed this!
         ('в % к соответствующему периоду предыдущего года', 'yoy'),
         ('в % к соответствующему месяцу предыдущего года', 'yoy'),
         ('млн.рублей', 'mln_rub'),
         ('отчетный месяц в % к предыдущему месяцу', 'rog'),         
         ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
         ('период с начала отчетного года', 'ytd'),
         ('рублей / rubles', 'rub')])


exclude = ["IMPORT_GOODS__TOTAL_yoy", "IMPORT__GOODS_TOTAL_rog",
           "EXPORT_GOODS__TOTAL_yoy", "EXPORT__GOODS_TOTAL_rog"]
    
class Definition():    
    def __init__(self, name):        
        self.name = name
        self.headers = odict()        
        self.markers = []
        self.reader = None
        self.required = []
        
    def add_header(self, text, varname):
        self.headers.update(odict({text: varname})) 

    def add_marker(self, _start, _end):
        self.markers.append(odict(start=_start, end=_end))
    
    def add_reader(self, funcname):
        self.reader = funcname
        
    def __str__(self):
        return self.name + "({})".format(len(self.required))
    
    def __repr__(self):
        return self.__str__()
    
    # FIXME: may depreciate?    
#    def varnames(self):
#        return list(set(v for v in self.headers.values()))    
    
    def require(self, varname, unit):
        self.required.append((varname, unit))
        
    def validate(self):
        pass

class Specification:
    def __init__(self, pdef_main):
        self.main = pdef_main
        self.additional = []
        
    def append(self, pdef):
        self.additional.append(pdef) 
        
    # FIXME: may depreciate?    
#    def varnames(self):
#        vns = set()
#        for pdef in [self.main] + self.additional:
#            for x in pdef.varnames():
#                vns.add(x)
#        return list(vns)        

    def validate(self):
        pass
    
    # TODO validate specification - order of markers 
    # - ends are after starts
    # - sorted starts follow each other 
    # - varnames match .required()
    
    def required(self):
        for pdef in [self.main] + self.additional:
            for req in pdef.required:
                yield req
        
    def __str__(self): 
        listing = ", ".join(d.__str__() for d in self.additional)
        cnt = len(list(self.required()))
        return ("<Required variables: {}".format(cnt) +
              "\n Parsing defintions: [{}]".format(listing) +
              "\n Default definition: {}>".format(self.main.__str__())
              )
        
        
d = Definition("MAIN")
d.add_header("Объем ВВП", "GDP")
d.add_header("Валовой внутренний продукт", "GDP")
d.add_header("Индекс физического объема произведенного ВВП, в %", "GDP")
d.add_header("Индекс промышленного производства", "IND_PROD")
# WARNING: may add many IND_PROD if no end specified below
d.add_marker(None, "1.2.1. Индексы производства по видам деятельности")
d.require("GDP", "bln_rub")
d.require("GDP", "yoy")
d.require("IND_PROD", "yoy")
d.require("IND_PROD", "rog")
d.require("IND_PROD", "ytd")
spec = Specification(d)


d = Definition("EXIM")
d.add_marker("1.9. Внешнеторговый оборот – всего"
           , "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего"
           , "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего"
           , "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья")
d.add_header("экспорт товаров – всего", "EXPORT_GOODS_TOTAL")
d.add_header("импорт товаров – всего", "IMPORT_GOODS_TOTAL")
d.require("EXPORT_GOODS_TOTAL", "bln_usd")
d.require("IMPORT_GOODS_TOTAL", "bln_usd")
spec.append(d)


d = Definition("GOV_REVENUE_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.1. Доходы (по данным Федерального казначейства)"
           , "2.1.2. Расходы (по данным Федерального казначейства)")
d.add_header("Консолидированный бюджет", "GOV_REVENUE_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет", "GOV_REVENUE_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_REVENUE_ACCUM_SUBFEDERAL")
d.require("GOV_REVENUE_ACCUM_CONSOLIDATED", "bln_rub") 
d.require("GOV_REVENUE_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_REVENUE_ACCUM_SUBFEDERAL", "bln_rub")
spec.append(d)


d = Definition("GOV_EXPENSE_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.2. Расходы (по данным Федерального казначейства)"
           , "2.1.3. Превышение доходов над расходами")
d.add_header("Консолидированный бюджет", "GOV_EXPENSE_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет", "GOV_EXPENSE_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_EXPENSE_ACCUM_SUBFEDERAL")
d.require("GOV_EXPENSE_ACCUM_CONSOLIDATED", "bln_rub") 
d.require("GOV_EXPENSE_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_EXPENSE_ACCUM_SUBFEDERAL", "bln_rub")
spec.append(d)


d = Definition("GOV_SURPLUS_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.3. Превышение доходов над расходами"
           , "2.2. Сальдированный финансовый результат")
d.add_header("Консолидированный бюджет", "GOV_SURPLUS_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет", "GOV_SURPLUS_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_SURPLUS_ACCUM_SUBFEDERAL")
d.require("GOV_SURPLUS_ACCUM_CONSOLIDATED", "bln_rub") 
d.require("GOV_SURPLUS_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_SURPLUS_ACCUM_SUBFEDERAL", "bln_rub")
spec.append(d)

d = Definition("RETAIL_SALES")
d.add_marker("1.13. Оборот розничной торговли, млрд.рублей"
           , "1.13.1. Оборот общественного питания, млрд.рублей")
d.add_marker("1.12. Оборот розничной торговли, млрд.рублей"
           , "1.12.1. Оборот общественного питания, млрд.рублей")
d.add_header("Оборот розничной торговли", "RETAIL_SALES")
d.add_header("пищевые продукты, включая напитки, и табачные изделия", "RETAIL_SALES_FOOD")
d.add_header("непродовольственные товары", "RETAIL_SALES_NONFOODS")
d.require("RETAIL_SALES", "bln_rub") 
d.require("RETAIL_SALES_FOOD", "bln_rub")
d.require("RETAIL_SALES_NONFOODS", "bln_rub")
d.require("GOV_SURPLUS_ACCUM_SUBFEDERAL", "bln_rub")
spec.append(d)

#FIXME: does nothing yet
spec.validate()
print(spec)

if __name__ == "__main__":
    #init_dirs(processed)
    #init_dirs(rosstat_folder)
    pass