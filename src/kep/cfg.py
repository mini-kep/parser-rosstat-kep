# -*- coding: utf-8 -*-
"""Parsing specification is *units* dict and *spec*, Specification() instance.

*UNITS* is to detect units of measurement in table headers (like "мдрд.руб.")

*spec* is Specification() instance, containing main and additional parsing
definitions. Yes, it seems to be a singleton.

A parsing definition consists of:
 (a) parsing boundaries - start and end lines CSV file segment
     where definition applies (self.markers)
 (b) a dictionary linking table headers ("Объем ВВП") and variable names
     ("GDP")
 (с) reader function name, for some unusual tables.

"""

from collections import OrderedDict as odict

# units of measurement
UNITS = odict([('млрд.долларов', 'bln_usd'),
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

UNIT_NAMES = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'rub': 'руб.',
              'rog': '% к предыдущему периоду',
              'yoy': '% к соответствующему месяцу предыдущего года',
              'ytd': 'период с начала отчетного года'}

# check 1: all units have a common short name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())


class Definition():
    """Parsing defintion contains:
       - csv line boundaries
       - text to match with variable name 
       - required variable names
       - reader function name for unusual table formats (optional)"""
    def __init__(self, name):
        # Definion name  
        self.name = name
        self.headers = odict()
        self.markers = []
        self.reader = None
        self.required = []

    def add_header(self, text, varname):
        # linking table header line ("Объем ВВП") to variable name ("GDP")
        self.headers.update(odict({text: varname}))

    def add_marker(self, _start, _end, must_check=True):
        # start and end lines CSV file segment  where defintion applies
        if must_check:
            if _start is None and _end is not None:
                raise ValueError("Markers not supported")
            if _start is not None and _end is None:
                raise ValueError("Markers not supported")
        self.markers.append(odict(start=_start, end=_end))

    def add_reader(self, funcname):
        # reader function name, for some unusual tables
        self.reader = funcname

    def __str__(self):
        return self.name + "({})".format(len(self.required))

    def __repr__(self):
        return self.__str__()

    def varnames(self):
        gen = self.headers.values()
        return list(set(v for v in gen))

    def require(self, varname, unit):
        # require occurrence of varibale lable defined by varibale name and unit of measurement
        # eg 'GDP', 'rog'
        # only required variables will be imported to final dataset
        self.required.append((varname, unit))


class Specification:
    """Specification holds a list of defintions in two variables:
       .main (default definition)
       .additional (other defintitions)
    """
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
        # FIXME: make sure markers are sorted
        pass
        # TODO: validate specification - order of markers
        # - ends are after starts
        # - sorted starts follow each other

    def required(self):
        for pdef in [self.main] + self.additional:
            for req in pdef.required:
                yield req

    def count_vars(self):
        return len(list(self.required()))

    def count_defs(self):
        return len(self.additional + [self.main])

    def __str__(self):
        listing = ", ".join(d.__str__() for d in self.additional + [self.main])
        cnt1 = self.count_vars()
        cnt2 = self.count_defs()
        pat = "{} required variables in {} parsing definitions {}"
        return (pat.format(cnt1, cnt2, listing))

    def __repr__(self):
        return "{}({})".format(self.__class__, self.__str__())


d = Definition("MAIN")
d.add_header("Объем ВВП", "GDP")
d.add_header("Валовой внутренний продукт", "GDP")
d.add_header("Индекс физического объема произведенного ВВП, в %", "GDP")
d.add_header("Индекс промышленного производства", "IND_PROD")
d.add_marker(None, None)
d.require("GDP", "bln_rub")
d.require("GDP", "yoy")
d.require("IND_PROD", "yoy")
d.require("IND_PROD", "rog")
d.require("IND_PROD", "ytd")
SPEC = Specification(d)


d = Definition("EXIM")
d.add_marker("1.9. Внешнеторговый оборот – всего",
             "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего",
             "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего",
             "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья")
d.add_header("экспорт товаров – всего", "EXPORT_GOODS_TOTAL")
d.add_header("импорт товаров – всего", "IMPORT_GOODS_TOTAL")
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
d.add_header("Оборот розничной торговли", "RETAIL_SALES")
d.add_header("продовольственные товары", "RETAIL_SALES_FOOD")
d.add_header(
    "пищевые продукты, включая напитки и табачные изделия",
    "RETAIL_SALES_FOOD")
d.add_header(
    "пищевые продукты, включая напитки, и табачные изделия",
    "RETAIL_SALES_FOOD")
d.add_header("непродовольственные товары", "RETAIL_SALES_NONFOODS")
d.require("RETAIL_SALES", "bln_rub")
d.require("RETAIL_SALES_FOOD", "bln_rub")
d.require("RETAIL_SALES_NONFOODS", "bln_rub")
SPEC.append(d)

# FIXME: does nothing yet
SPEC.validate()
# units and spec are ready to use are parsing inputs
print(SPEC)


# variable descriptions for frontend
DESC = {
    "GDP": "Валовой внутренний продукт",
    "IND_PROD": "Промышленное производство",
    "EXPORT_GOODS_TOTAL": "Экспорт товаров - всего",
    "IMPORT_GOODS_TOTAL": "Импорт товаров - всего",
    "RETAIL_SALES": "Оборот розничной торговли - всего",
    "RETAIL_SALES_FOOD": "Оборот розничной торговли - продовольственные товары",
    "RETAIL_SALES_NONFOODS": "Оборот розничной торговли - непродовольственные товары"}

# check 2: check all spec.required are listed in desc_dict and vice versus
# assert set(desc.keys()) == set(x for x, y in spec.required())

a = set(DESC.keys())
b = set(x for x, y in SPEC.required())
not_in_a = set(x for x in b if x not in a)
not_in_b = set(x for x in a if x not in b)

# FIXME: in final version not_in_a must equal to set()
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

# groups of variables for frontend
SECTIONS = odict([
    ("ВВП и производство", ["GDP", "IND_PROD"]),
    ("Внешняя торговля", ["EXPORT_GOODS_TOTAL",
                          "IMPORT_GOODS_TOTAL"]),
    ("Розничная торговля", ["RETAIL_SALES",
                            "RETAIL_SALES_FOOD",
                            "RETAIL_SALES_NONFOODS"])
])

# TODO:can make it a class
# class Sections:
#    """Grouping of variables to report at frontend"""

# check 3: sections includes all items in description
z = list()
[z.extend(labels) for labels in SECTIONS.values()]
assert set(z) == set(DESC.keys())


def yield_variable_descriptions_with_subheaders(sections=SECTIONS,
                                                desc=DESC):
    def bold(s):
        return"**{}**".format(s)
    for section_name, labels in sections.items():
        yield([bold(section_name), ""])
        for label in labels:
            yield([desc[label], label])


if __name__ == "__main__":
    pass