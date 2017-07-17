# -*- coding: utf-8 -*-
"""Parsing instruction contains:
       - text to match with variable name
       - required variable names
       - csv line boundaries (optional)
       - reader function name for unusual table formats (optional)"""

from collections import OrderedDict as odict

# mapper dictionary to convert text in table headers to unit of measurement
UNITS = odict([  # 1. MONEY
    ('млрд.долларов', 'bln_usd'),
    ('млрд. долларов', 'bln_usd'),
    ('млрд, долларов', 'bln_usd'),
    ('млрд.рублей', 'bln_rub'),
    ('млрд. рублей', 'bln_rub'),
    ('рублей / rubles', 'rub'),
    ('млн.рублей', 'mln_rub'),
    # 2. RATES OF CHANGE
    ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
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
    ('отчетный месяц в % к предыдущему месяцу', 'rog'),
    ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
    ('период с начала отчетного года', 'ytd'),
    # 3. OTHER UNITS (keep below RATES OF CHANGE)
    ('%', 'pct'),
    ('в % к ВВП', 'gdp_percent'),
    # 4. stub for CPI section
    ("продукты питания", 'rog'),
    ("алкогольные напитки", 'rog'),
    ("непродовольственные товары", 'rog'),
    ("непродовольст- венные товары", 'rog'),
    ("услуги", 'rog')
])

# 'official' names of units used in project front
UNIT_NAMES = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'rub': 'руб.',
              'rog': '% к пред. периоду',
              'yoy': '% год к году',
              'ytd': 'период с начала года',
              'pct': '%'}

# check: all units in mapper dict have an 'offical' name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())


class Indicator:
    """An economic indicator parsing instructions"""

    def __init__(self, varname, text, required_units, desc=None, sample=None):
        """Parameters:
        varname        - variable name string like 'GDP', 'CPI', etc
        text           - string(s) found in table header in CSV files 
                         examples: 'Объем ВВП', 'Gross domestic product'  
        required_units - unit(s) of measurement required for this indicator
                         examples: 'rog', ['rog'],  ['bln_rub', 'yoy']
        desc           - indicator desciption string for frontpage
        sample         - control string - one of raw CSV file rows (not implemented)"""
        
        self.varname = varname
        text = self.as_list(text)
        # construct mapper dictionary
        self.headers = odict([(t, self.varname) for t in text])
        # construct labels
        ru = self.as_list(required_units)
        self.required = [(self.varname, unit) for unit in ru]
        # optional description
        if desc:
            self.desc = desc
        else:
            self.desc = text[0]
        # TODO: make use of sample string in parsing    
        self.sample = sample    
        
    def __eq__(self, x):
        return bool(self.required == x.required and self.headers == x.headers)

    def __repr__(self):
        text = [x for x in self.headers.keys()]
        req = [x[1] for x in self.required]
        args = "'{}', {}, {}, '{}'".format(self.varname, text, req, self.desc)
        return "Indicator ({})".format(args)

    @staticmethod
    def as_list(x):
        if isinstance(x, str):
            return [x]
        else:
            return x


class Definition:

    def __init__(self, reader=None):
        self.indicators = []
        self.reader = reader

    def append(self, *args, **kwargs):
        pdef = Indicator(*args, **kwargs)
        self.indicators.append(pdef)

    @property
    def headers(self):
        def _yield():
            for ind in self.indicators:
                for k, v in ind.headers.items():
                    yield k, v
        return odict(list(_yield()))

    @property
    def required(self):
        def _yield():
            for ind in self.indicators:
                for req in ind.required:
                    yield req
        return list(_yield())

    def varnames(self):
        return [ind.varname for ind in self.indicators]

    def __eq__(self, x):
        return bool(self.indicators == x.indicators and self.reader == x.reader)

    def __repr__(self):
        vns = ", ".join(self.varnames())
        return "Definition for {}".format(vns)


class Scope():
    """Start and end lines for CSV file segment and associated variables
       defintion.

       Holds several versions of start and end line, return applicable line
       for a particular CSV file versions. This solves problem of different
       headers for same table at various releases.
    """

    def __init__(self, start, end, reader=None):
        self.__markers = []
        self.add_bounds(start, end)
        self.definition = Definition(reader)

    def add_bounds(self, start, end):
        if start and end:
            self.__markers.append(dict(start=start, end=end))
        else:
            raise ValueError("Cannot accept empty line as Scope() boundary")

    def append(self, *args, **kwargs):
        self.definition.append(*args, **kwargs)

    def get_parsing_definition(self):
        return self.definition

    def __repr__(self):
        msg1 = repr(self.definition)
        s = self.__markers[0]['start'][:10]
        e = self.__markers[0]['end'][:10]
        msg2 = "bound by start <{}...>, end <{}...>".format(s, e)
        return " ".join([msg1, msg2])

    def get_bounds(self, rows):
        """Get start and end line markers, which can be found in *rows*"""
        rows = [r for r in rows]  # consume iterator
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            if self.__is_found(s, rows) and self.__is_found(e, rows):
                return s, e
        msg = self.__error_message(rows)
        raise ValueError(msg)

    @staticmethod
    def __is_found(line, rows):
        """Return True, is *line* found at start of any entry in *rows*"""
        for r in rows:
            if r.startswith(line):
                return True
        return False

    def __error_message(self, rows):
        msg = []
        msg.append("start or end line not found in *rows*")
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            msg.append("is_found: {} <{}>".format(self.__is_found(s, rows), s))
            msg.append("is_found: {} <{}>".format(self.__is_found(e, rows), e))
        return "\n".join(msg)


class Specification:
    """Specification holds a list of defintions in two variables:

       .main ()
       .scope (segment defintitions)
    """

    def __init__(self, pdef):
        # main parsing definition, Definition
        self.main = pdef
        # local parsing definitions for segments
        self.scopes = []

    def add_scope(self, scope):
        self.scopes.append(scope)
        self.validate()

    def get_main_parsing_definition(self):
        return self.main

    def __all_definitions(self):
        return [self.main] + [sc.definition for sc in self.scopes]

    def varnames(self):
        varnames = set()
        for pdef in self.__all_definitions():
            for x in pdef.varnames():
                varnames.add(x)
        return sorted(list(varnames))

    def validate(self):
        # FIXME: order of markers - ends are not starts
        pass

    def required(self):
        for pdef in self.__all_definitions():
            for req in pdef.required:
                yield req

# global parsing defintion
main = Definition()
main.append(varname="GDP",
            text=["Oбъем ВВП",
                  "Индекс физического объема произведенного ВВП, в %",
                  "Валовой внутренний продукт"],
            required_units=["bln_rub", "yoy"],
            desc="Валовый внутренний продукт (ВВП)",
            sample="1999	4823	901	1102	1373	1447")
main.append(varname="INDPRO",
            text="Индекс промышленного производства",
            required_units=["yoy", "rog"],
            desc="Промышленное производство")
SPEC = Specification(main)

# segment definitions

# investment
sc = Scope("1.6. Инвестиции в основной капитал",
           "1.6.1. Инвестиции в основной капитал организаций")
sc.add_bounds("1.7. Инвестиции в основной капитал",
              "1.7.1. Инвестиции в основной капитал организаций")
sc.append("INVESTMENT",
          "Инвестиции в основной капитал", 
          ["bln_rub", "yoy", "rog"])
SPEC.add_scope(sc)

# export/import
sc = Scope("1.9. Внешнеторговый оборот – всего",
           "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
sc.add_bounds("1.10. Внешнеторговый оборот – всего",
              "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
sc.append(text="экспорт товаров – всего",
          varname="EXPORT_GOODS",
          required_units="bln_usd",
          desc="Экспорт товаров")
sc.append(text="импорт товаров – всего",
          varname="IMPORT_GOODS",
          required_units="bln_usd",
          desc="Импорт товаров")
SPEC.add_scope(sc)

# inflation
sc = Scope(start="3.5. Индекс потребительских цен",
           end="4. Социальная сфера")
sc.append("CPI",
          text="Индекс потребительских цен",
          required_units="rog",
          desc="Индекс потребительских цен (ИПЦ)")
sc.append("CPI_NONFOOD",
          text=["непродовольственные товары",
                "непродовольст- венные товары"],
          required_units="rog",
          desc="ИПЦ (непродтовары)")
sc.append("CPI_FOOD",
          text="продукты питания",
          required_units="rog",
          desc="ИПЦ (продтовары)")
sc.append("CPI_ALC",
          text="алкогольные напитки",
          required_units="rog",
          desc="ИПЦ (алкоголь)")
sc.append("CPI_SERVICES",
          text="услуги",
          required_units="rog",
          desc="ИПЦ (услуги)")
SPEC.add_scope(sc)

    # TODO:
    # - [ ] migrate existing definitions to this file    
    # NOT TODO:
    # - [ ] spec validation procedure
    # - [ ] use of sample row
    # - [ ] think of a better pattern to create SPEC


if __name__ == "__main__":
    pass
