# -*- coding: utf-8 -*-
"""
units
spec 
desc
sections
"""
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
         #       ... must precede this
         # because 'в % к предыдущему периоду' is found in 
         # 'период с начала отчетного года в % к соответствующему периоду предыдущего года'
         ('в % к соответствующему периоду предыдущего года', 'yoy'),
         ('в % к соответствующему месяцу предыдущего года', 'yoy'),
         ('млн.рублей', 'mln_rub'),
         ('отчетный месяц в % к предыдущему месяцу', 'rog'),         
         ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
         ('период с начала отчетного года', 'ytd'),
         ('рублей / rubles', 'rub')])

unit_names = {'bln_rub': 'млрд.руб.', 
 'bln_usd': 'млрд.долл.', 
 'gdp_percent': '% ВВП', 
 'mln_rub': 'млн.руб.',  
 'rub': 'руб.', 
 'rog': '% к предыдущему периоду',
 'yoy': '% к соответствующему месяцу предыдущего года', 
 'ytd': 'период с начала отчетного года'}

# check 1: all units have a common name 
assert set(unit_names.keys()) == set(units.values())
    
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

#WONTFIX: some supplementary parsing results are ignored, e.g.
# "IMPORT_GOODS_TOTAL_yoy", "IMPORT_GOODS_TOTAL_rog",
# "EXPORT_GOODS_TOTAL_yoy", "EXPORT_GOODS_TOTAL_rog"

#FIXME: spec.validate() does nothing yet
    # TODO validate specification - order of markers 
    # - ends are after starts
    # - sorted starts follow each other 
    # - varnames match .required()

spec.validate()
print(spec)
    

desc_list = [["Валовой внутренний продукт", "GDP"],
        ["Промышленное производство", "IND_PROD"],
        ["Экспорт товаров - всего", "EXPORT_GOODS_TOTAL"],
        ["Импорт товаров - всего", "IMPORT_GOODS_TOTAL"],
        ["Оборот розничной торговли - всего", "RETAIL_SALES"],
        ["Оборот розничной торговли - продовольственные товары", "RETAIL_SALES_FOOD"],
        ["Оборот розничной торговли - непродовольственные товары", "RETAIL_SALES_NONFOODS"]
]

desc = {d[1]:d[0] for d in desc_list} 

#check 2: check all spec.required are listed in desc_dict and vice versus
# assert set(desc.keys()) == set(x for x, y in spec.required())

a = set(desc.keys())
b = set(x for x, y in spec.required())
not_in_a = set(x for x in b if x not in a)
not_in_b = set(x for x in a if x not in b)

# FIXME: in final version not_in_a must equal to set()
assert not_in_a == {'GOV_EXPENSE_ACCUM_CONSOLIDATED', 'GOV_EXPENSE_ACCUM_FEDERAL', 'GOV_EXPENSE_ACCUM_SUBFEDERAL',
                    'GOV_REVENUE_ACCUM_CONSOLIDATED', 'GOV_REVENUE_ACCUM_FEDERAL', 'GOV_REVENUE_ACCUM_SUBFEDERAL',
                    'GOV_SURPLUS_ACCUM_FEDERAL', 'GOV_SURPLUS_ACCUM_SUBFEDERAL'}
assert not_in_b == set() 


sections = odict([
           ("ВВП и производство", ["GDP", "IND_PROD"]),             
           ("Внешняя торговля",   ["EXPORT_GOODS_TOTAL",
                                   "IMPORT_GOODS_TOTAL"]),       
           ("Розничная торговля", ["RETAIL_SALES",
                                   "RETAIL_SALES_FOOD",
                                   "RETAIL_SALES_NONFOODS"])
])
    
#check 3: sections includes all items in description 
# FIXME: maybe more elegant unpacking below (?)
z = list()
[z.extend(labels) for labels in sections.values()]

#алтернативный вариант:
#from operator import concat
#from functools import reduce
#z = reduce(concat, sections.values())

assert set(z) == set(desc.keys())

def bold(s):
    return "**{}**".format(s)

def yield_variable_descriptions_with_subheaders(sections = sections):
    for section_name, labels in sections.items(): 
         yield([bold(section_name), ""])            
         for label in labels: 
              yield([desc[label], label])           

if __name__ == "__main__":
    pass
