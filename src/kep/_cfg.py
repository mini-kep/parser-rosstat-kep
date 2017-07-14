# -*- coding: utf-8 -*-
"""Parsing specification:

  *UNITS* maps parts of headers like "мдрд.руб." to "bln_rub"

  *spec* - Specification() instance, containing main and additional parsing
           definitions. Yes, it seems to be a singleton.
"""

from collections import OrderedDict as odict
import itertools

# TODO: maybe units should not be a global, but rather a part of pdef 
# units of measurement
UNITS = odict([('млрд.долларов', 'bln_usd'),
               ('млрд. долларов', 'bln_usd'),
               ('млрд, долларов', 'bln_usd'),
               ('млрд.рублей', 'bln_rub'),
               ('млрд. рублей', 'bln_rub'),
               ('рублей / rubles', 'rub'),
               
               ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
               ('в % к ВВП', 'gdp_percent'),
               ('в % к декабрю предыдущего года', 'ytd'),
               ('в % к предыдущему месяцу', 'rog'),
               ('в % к предыдущему периоду', 'rog'),
               ('% к концу предыдущего периода', 'rog'),
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
               ('%', 'pct'),               
               
               # -- stub for CPI section---
               ("продукты питания", 'rog'),
               ("алкогольные напитки", 'rog'),
               ("непродовольственные товары", 'rog'),
               ("непродовольст- венные товары", 'rog'),
               ("услуги", 'rog')               
               ])

UNIT_NAMES = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'rub': 'руб.',
              'rog': '% к пред. периоду',
              'yoy': '% год к году',
              'ytd': 'период с начала года',
              'pct': '%'}

# check 1: all units have a common short name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())


# start and end lines
def is_found(line, rows):
    """Return True, is *line* found at start of any entry in *rows*""" 
    for r in rows:
        if r.startswith(line):
            return True
    return False 

class Scope():
    """Start and end lines CSV file segment. 
    
       May hold and manupulate several versions of start and end line,
       applicable to different csv file versions.
       
       Solves problem of different headers for same table at various 
       data releases.
       
       Will use methods like:
       .add_marker("1.9. Внешнеторговый оборот – всего",
                "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
       .add_marker("1.10. Внешнеторговый оборот – всего",
                "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
    """
    
    def __init__(self):        
        self.markers = []
   
    def add_marker(self, start, end):        
        if start and end:
            self.markers.append(dict(start=start, end=end))
        else:
            raise ValueError("Cannot accept empty line for Scope() boundary")
            
    def get_boundaries(self, rows):
        ix = self.__get_marker_index__(rows)
        if ix is not None:
            marker = self.markers[ix]
            return marker['start'], marker['end']
        else:
            msg = self.__error_message__(rows)  
            raise ValueError(msg)
   
    def __get_marker_index__(self, rows):
        """Identify which pair of markers applies to *rows*."""
        rows = [r for r in rows] # consume iterator
        for i, marker in enumerate(self.markers):
            s = marker['start']
            e = marker['end']            
            if is_found(s, rows) and is_found(e, rows):
               return i
        return None        

    def __error_message__(self, rows):
        msg = []
        msg.append("start or end line not found in *rows*")
        for marker in self.markers:
            s = marker['start']
            e = marker['end']
            msg.append("   {} <{}>".format(is_found(s, rows), s))
            msg.append("   {} <{}>".format(is_found(e, rows), e))
        return "\n".join(msg)
            
class Definition():
    """Parsing defintion contains:
       - text to match with variable name
       - required variable names
       - csv line boundaries (optional)
       - reader function name for unusual table formats (optional)"""

    def __init__(self, name):
        self.name = name
        # mandatory
        self.headers = odict()
        self.required = []
        # optional
        self.scope = Scope()
        self.reader = None
        self.reference_names = {}

    def add_header(self, text, varname, ref=False):
        # linking table header line ("Объем ВВП") to variable name ("GDP")
        self.headers.update(odict({text: varname}))
        if ref:
            self.add_desc(text, varname)   
            
    def add_desc(self, text, varname): 
        self.reference_names.update({varname:text})          

    def require(self, varname, unit):
        # require occurrence of varibale lable defined by varibale name and 
        # unit of measurement eg 'GDP', 'rog'
        # only required variables will be imported to final dataset
        self.required.append((varname, unit))

    def add_marker(self, start, end):
        # start and end lines CSV file segment  where defintion applies
        self.scope.add_marker(start, end)

    def add_reader(self, funcname):
        # reader function name, for some unusual tables
        self.reader = funcname

    def __str__(self):
        return  "{}({})".format(self.name, len(self.required))

    def __repr__(self):
        return self.__str__()

    def varnames(self):
        gen = list(self.headers.values())
        return list(set(gen))
    

class Specification:
    """Specification holds a list of defintions in two variables:
        
       .main (default definition)
       .additional (segment defintitions)
       
    """

    def __init__(self, pdef_main):
        self.main = pdef_main
        self.segments = []
        
    def all_definitions(self):
        return [self.main] + self.segments

    def append(self, pdef):
        self.segments.append(pdef)

    def varnames(self):
        varnames = set()
        for pdef in self.all_definitions():
            for x in pdef.varnames():
                varnames.add(x)
        return sorted(list(varnames))

    def validate(self, rows):
        # TODO: validate specification - order of markers
        # - ends are after starts
        # - sorted end-starts follow each other
        pass

    def required(self):
        for pdef in self.all_definitions():
            for req in pdef.required:
                yield req

    def count_vars(self):
        return len(list(self.required()))

    def count_defs(self):
        return len(self.all_definitions())

    def __str__(self):
        cnt1 = self.count_vars()
        cnt2 = self.count_defs()
        pat = "{} required variables in {} parsing definitions".format(cnt1, cnt2)
        listing1 = ", ".join([str(d) for d in self.segments])
        segs = "Segment definitions: {}".format(listing1)
        main = "Main definition: {}".format(self.main)
        return "{}\n{}\n{}".format(pat, segs, main)

    def __repr__(self):
        return "{}({})".format(self.__class__, self.__str__())
    
    def reference_names(self):
        d = {}
        for pdef in self.all_definitions():
            d = {**d, **pdef.reference_names}
        return d 

d = Definition("MAIN")
d.add_header("Валовой внутренний продукт", "GDP", True)
d.add_header("Объем ВВП", "GDP")
d.add_header("Индекс физического объема произведенного ВВП, в %", "GDP")
d.require("GDP", "bln_rub")
d.require("GDP", "yoy")
# TODO: rename to IP
d.add_header("Индекс промышленного производства", "IND_PROD", True)
d.require("IND_PROD", "yoy")
d.require("IND_PROD", "rog")
#d.add_header("Уровень безработицы в возрасте 15-72 лет", "UNEMPL")
d.add_header("Уровень безработицы", "UNEMPL", True)
d.require("UNEMPL", "pct")
d.add_header("Среднемесячная номинальная начисленная заработная плата работников организаций", 
             "WAGE_NOMINAL")
d.add_desc("Среднемесячная заработная плата", "WAGE_NOMINAL")
d.require("WAGE_NOMINAL", "rub")
d.add_header("Реальная начисленная заработная плата работников организаций",
             "WAGE_REAL")
d.add_desc("Реальная заработная плата", "WAGE_REAL")
d.require("WAGE_REAL", "rog")
d.require("WAGE_REAL", "yoy")

#d.add_header("Коммерческий грузооборот транспорта", "TRANSPORT_FREIGHT", ref=True)
#d.require("UNEMPL", "pct")

SPEC = Specification(d)


# Коммерческий грузооборот транспорта, млрд. тонно-км / Commercial freight turnover, bln ton-km	
d = Definition("INVEST")
d.add_marker("1.6. Инвестиции в основной капитал",
             "1.6.1. Инвестиции в основной капитал организаций")             
d.add_marker("1.7. Инвестиции в основной капитал",
             "1.7.1. Инвестиции в основной капитал организаций")
d.add_header("Инвестиции в основной капитал", "INVESTMENT", True)
d.require("INVESTMENT", "bln_rub")
d.require("INVESTMENT", "yoy")
d.require("INVESTMENT", "rog")
SPEC.append(d)


d = Definition("EXIM")
d.add_marker("1.9. Внешнеторговый оборот – всего",
             "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего",
             "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего",
             "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья")
d.add_header("экспорт товаров – всего", "EXPORT_GOODS_TOTAL")
d.add_header("импорт товаров – всего", "IMPORT_GOODS_TOTAL")
d.add_desc("Экспорт товаров", "EXPORT_GOODS_TOTAL")
d.add_desc("Импорт товаров", "IMPORT_GOODS_TOTAL")
d.require("EXPORT_GOODS_TOTAL", "bln_usd")
d.require("IMPORT_GOODS_TOTAL", "bln_usd")
SPEC.append(d)


d = Definition("GOV_REVENUE_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.1. Доходы (по данным Федерального казначейства)",
             "2.1.2. Расходы (по данным Федерального казначейства)")
d.add_header("Консолидированный бюджет", "GOV_REVENUE_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет", "GOV_REVENUE_ACCUM_FEDERAL")
d.add_header(
    "Консолидированные бюджеты субъектов Российской Федерации",
    "GOV_REVENUE_ACCUM_SUBFEDERAL")
d.require("GOV_REVENUE_ACCUM_CONSOLIDATED", "bln_rub")
d.require("GOV_REVENUE_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_REVENUE_ACCUM_SUBFEDERAL", "bln_rub")
SPEC.append(d)


d = Definition("GOV_EXPENSE_ACCUM")
d.add_reader("fiscal")
d.add_marker(
    "2.1.2. Расходы (по данным Федерального казначейства)",
    "2.1.3. Превышение доходов над расходами")
d.add_header("Консолидированный бюджет", "GOV_EXPENSE_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет", "GOV_EXPENSE_ACCUM_FEDERAL")
d.add_header(
    "Консолидированные бюджеты субъектов Российской Федерации",
    "GOV_EXPENSE_ACCUM_SUBFEDERAL")
d.require("GOV_EXPENSE_ACCUM_CONSOLIDATED", "bln_rub")
d.require("GOV_EXPENSE_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_EXPENSE_ACCUM_SUBFEDERAL", "bln_rub")
SPEC.append(d)


d = Definition("GOV_SURPLUS_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.3. Превышение доходов над расходами",
             "2.2. Сальдированный финансовый результат")
d.add_header("Федеральный бюджет", "GOV_SURPLUS_ACCUM_FEDERAL")
d.add_header(
    "Консолидированные бюджеты субъектов Российской Федерации",
    "GOV_SURPLUS_ACCUM_SUBFEDERAL")
d.require("GOV_SURPLUS_ACCUM_FEDERAL", "bln_rub")
d.require("GOV_SURPLUS_ACCUM_SUBFEDERAL", "bln_rub")
SPEC.append(d)

d = Definition("RETAIL_SALES")
d.add_marker("1.12. Оборот розничной торговли",
             "1.12.1. Оборот общественного питания")
d.add_marker("1.13. Оборот розничной торговли",
             "1.13.1. Оборот общественного питания")
d.add_header("Оборот розничной торговли", "RETAIL_SALES", True)
d.add_header("продовольственные товары", "RETAIL_SALES_FOOD")
d.add_header(
    "пищевые продукты, включая напитки и табачные изделия",
    "RETAIL_SALES_FOOD")
d.add_header(
    "пищевые продукты, включая напитки, и табачные изделия",
    "RETAIL_SALES_FOOD")
d.add_header("непродовольственные товары", "RETAIL_SALES_NONFOODS")
d.add_desc("Оборот розничной торговли (продтовары)", "RETAIL_SALES_FOOD")
d.add_desc("Оборот розничной торговли (непродтовары)", "RETAIL_SALES_NONFOODS")
d.require("RETAIL_SALES", "bln_rub")
d.require("RETAIL_SALES", "yoy")
d.require("RETAIL_SALES", "rog")
d.require("RETAIL_SALES_FOOD", "bln_rub")
d.require("RETAIL_SALES_FOOD", "yoy")
d.require("RETAIL_SALES_FOOD", "rog")
# TODO: change to RETAIL_SALES_NONFOOD
d.require("RETAIL_SALES_NONFOODS", "bln_rub")
d.require("RETAIL_SALES_NONFOODS", "yoy")
d.require("RETAIL_SALES_NONFOODS", "rog")
SPEC.append(d)


#d = Definition("PPI")


d = Definition("CPI")
d.add_marker(start="3.5. Индекс потребительских цен",
             end="4. Социальная сфера")
d.add_header("Индекс потребительских цен", "CPI", True)
d.add_header("продукты питания", "CPI_FOOD")
d.add_header("алкогольные напитки", "CPI_ALCOHOL")
d.add_header("непродовольственные товары", "CPI_NONFOOD")
d.add_header("непродовольст- венные товары", "CPI_NONFOOD")
d.add_header("услуги", "CPI_SERVICES")
d.add_desc("ИПЦ (продтовары)", "CPI_FOOD")
d.add_desc("ИПЦ (алкоголь)", "CPI_ALCOHOL")
d.add_desc("ИПЦ (непродтовары)", "CPI_NONFOOD")
d.add_desc("ИПЦ (услуги)", "CPI_SERVICES")
d.require("CPI", "rog")
d.require("CPI_FOOD", "rog")
d.require("CPI_NONFOOD", "rog")
d.require("CPI_ALCOHOL", "rog")
d.require("CPI_SERVICES", "rog")
SPEC.append(d)


# TODO: must check order of markers in additional definitions
SPEC.validate(None)

# units and spec are ready to use are parsing inputs
print(SPEC)

# variable descriptions
DESC = SPEC.reference_names()

# check 2: check all spec.required are listed in desc_dict and vice versus
# assert set(desc.keys()) == set(x for x, y in spec.required())

a = set(DESC.keys())
b = set(x for x, y in SPEC.required())
not_in_a = set(x for x in b if x not in a)
not_in_b = set(x for x in a if x not in b)
assert not_in_a == {
    'GOV_EXPENSE_ACCUM_CONSOLIDATED',
    'GOV_EXPENSE_ACCUM_FEDERAL',
    'GOV_EXPENSE_ACCUM_SUBFEDERAL',
    'GOV_REVENUE_ACCUM_CONSOLIDATED',
    'GOV_REVENUE_ACCUM_FEDERAL',
    'GOV_REVENUE_ACCUM_SUBFEDERAL',
    'GOV_SURPLUS_ACCUM_FEDERAL',
    'GOV_SURPLUS_ACCUM_SUBFEDERAL'}
assert not_in_b == set()


# frontend variable grouping
M_SECTIONS = odict([
    ("Производство",       ["IND_PROD_rog", "IND_PROD_yoy"]),
    ("Внешняя торговля",   ["EXPORT_GOODS_TOTAL_bln_usd", "IMPORT_GOODS_TOTAL_bln_usd"]),
    ("Розничная торговля", ["RETAIL_SALES_yoy", "RETAIL_SALES_FOOD_yoy", "RETAIL_SALES_NONFOODS_yoy"]),
    ("Социальная сфера",   ["UNEMPL"])
])


SECTIONS = odict([
    ("ВВП и производство", ["GDP", "IND_PROD"]),
    ("Инвестиции",         ["INVESTMENT"]),
    ("Внешняя торговля",   ["EXPORT_GOODS_TOTAL", "IMPORT_GOODS_TOTAL"]),
    ("Розничная торговля", ["RETAIL_SALES", "RETAIL_SALES_FOOD", "RETAIL_SALES_NONFOODS"]),
    ("Цены",               ["CPI", "CPI_FOOD", "CPI_NONFOOD", "CPI_ALCOHOL", "CPI_SERVICES"]),
    ("Население",          ["UNEMPL", 'WAGE_REAL', 'WAGE_NOMINAL']),
    ("Бюджет",             ['GOV_EXPENSE_ACCUM_CONSOLIDATED',
                            'GOV_EXPENSE_ACCUM_FEDERAL',
                            'GOV_EXPENSE_ACCUM_SUBFEDERAL',
                            'GOV_REVENUE_ACCUM_CONSOLIDATED',
                            'GOV_REVENUE_ACCUM_FEDERAL',
                            'GOV_REVENUE_ACCUM_SUBFEDERAL',
                            'GOV_SURPLUS_ACCUM_FEDERAL',
                            'GOV_SURPLUS_ACCUM_SUBFEDERAL'])
])

# check 3: sections includes all items in description
set1 = set(SPEC.varnames())
set2 = set(itertools.chain.from_iterable(SECTIONS.values()))
if set1 != set2:
    print("Must add to SECTIONS:", [x for x in set1 if x not in set2])


if __name__ == "__main__":
    sc = Scope()
    sc.add_marker("1.9. Внешнеторговый оборот – всего",
               "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
    sc.add_marker("1.10. Внешнеторговый оборот – всего",
                  "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
    sc.add_marker("1.10. Внешнеторговый оборот – всего",
                  "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья") 
