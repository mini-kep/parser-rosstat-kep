# -*- coding: utf-8 -*-
from collections import OrderedDict as odict   

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
         # ... must preceed this because 'в % к предыдущему периоду' is  found
         # in 'период с начала отчетного года в % к соответствующему периоду предыдущего года'
         ('в % к соответствующему периоду предыдущего года', 'yoy'),
         ('в % к соответствующему месяцу предыдущего года', 'yoy'),
         ('млн.рублей', 'mln_rub'),
         ('отчетный месяц в % к предыдущему месяцу', 'rog'),         
         ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
         ('период с начала отчетного года', 'ytd'),
         ('рублей / rubles', 'rub')])

#Some supplementary parsing results are ignored, e.g.
# "IMPORT_GOODS__TOTAL_yoy", "IMPORT__GOODS_TOTAL_rog",
# "EXPORT_GOODS__TOTAL_yoy", "EXPORT__GOODS_TOTAL_rog"
    
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
  
    def varnames(self):
        gen = self.headers.values()
        return list(set(v for v in gen))
    
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
        
    def varnames(self):
        varnames = set()
        for pdef in [self.main] + self.additional:
            for x in pdef.varnames():
                varnames.add(x)
        return sorted(list(varnames))

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
              "\nParsing definitions: {}".format(listing) +
              "\nDefault definition: {}>".format(self.main.__str__())
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
d.add_header("Федеральный бюджет", "GOV_SURPLUS_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_SURPLUS_ACCUM_SUBFEDERAL")
d.require("GOV_SURPLUS_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_SURPLUS_ACCUM_SUBFEDERAL", "bln_rub")
spec.append(d)

d = Definition("RETAIL_SALES")
d.add_marker("1.13. Оборот розничной торговли"
           , "1.13.1. Оборот общественного питания")
d.add_marker("1.12. Оборот розничной торговли"
           , "1.12.1. Оборот общественного питания")
d.add_header("Оборот розничной торговли", "RETAIL_SALES")
d.add_header("продовольственные товары", "RETAIL_SALES_FOOD")
d.add_header("пищевые продукты, включая напитки и табачные изделия", "RETAIL_SALES_FOOD")
d.add_header("пищевые продукты, включая напитки, и табачные изделия", "RETAIL_SALES_FOOD")
d.add_header("непродовольственные товары", "RETAIL_SALES_NONFOODS")
d.require("RETAIL_SALES", "bln_rub") 
d.require("RETAIL_SALES_FOOD", "bln_rub")
d.require("RETAIL_SALES_NONFOODS", "bln_rub")
spec.append(d)

#FIXME: does nothing yet
spec.validate()
print(spec)

if __name__ == "__main__":
    init_dirs(processed)
    init_dirs(rosstat_folder)
    pass