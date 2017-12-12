#FIXME: need new text
    
#"""Contains data structures used as parsing instructions.
#
#Global variable  **SPEC**  allows access to parsing definitions:
#
#  - :func:`csv2df.specification.Specification.get_main_parsing_definition` retrieves
#    main (default) parsing definition, where most indicators are defined;
#
#  - :func:`csv2df.specification.Specification.get_segment_parsing_definitions` provides
#    a list of parsing defintions by csv segment.
#
#**SPEC** is used by:
#
#  - :class:`csv2df.reader.RowStack`
#  - :func:`csv2df.parser.extract_tables`
#
#We parse CSV file by segment, because some table headers repeat themselves in
#CSV file. Extracting a piece out of CSV file gives a good isolated input for parsing.
#
#Previously parsing instructions were initialised from yaml file, but this led to many errors,
#so the parsing instructions are now created internally in *spec.py*.
#
#"""

from collections import OrderedDict as odict

from csv2df.util_label import make_label
from csv2df.util_row_splitter import FUNC_MAPPER


# mapper dictionary to convert text in table headers to unit of measurement
UNITS = odict([  # 1. MONEY
    ('млрд.долларов', 'bln_usd'),
    ('млрд. долларов', 'bln_usd'),
    ('млрд, долларов', 'bln_usd'),
    ('млрд.рублей', 'bln_rub'),
    ('млрд. рублей', 'bln_rub'),
    ('рублей / rubles', 'rub'),
    ('рублей', 'rub'),
    ('млн.рублей', 'mln_rub'),
    # 2. RATES OF CHANGE
    ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
    ('в % к декабрю предыдущего года', 'ytd'),
    ('в % к прошлому периоду', 'rog'),
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
    ("в % к экономически активному населению", "pct"),
    ('%', 'pct'),
    ('в % к ВВП', 'gdp_percent'),
    ('млрд. тонно-км', 'bln_tkm'),
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
              'pct': '%',
              'bln_tkm': 'млрд. тонно-км'}

# validation: all units in mapper dict have an 'offical' name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())


def as_list(x):  # : str): # not only str is intended input type
    """Transform string *x* to list *[x]*.

       Formats user input in ParsingInstruction class.

       Returns:
           list
    """
    if isinstance(x, list):
        return x
    elif isinstance(x, tuple):
        return list(x)
    else:
        return [x]


class Scope():
    """Delimit start and end line in CSV file.

       Holds several versions of start and end line, returns applicable lines
       for a particular CSV  versions. This solves problem of different
       headers for same table at various data releases.
    """

    def __init__(self, start, end):
        self.__markers = []
        self.add_bounds(start, end)

    def add_bounds(self, start, end):
        """Adds start and end bounds.

        Raises:
            ValueError: if any of input vars is empty string.
        """
        if start and end:
            self.__markers.append(dict(start=start, end=end))
        else:
            raise ValueError("Cannot accept empty line as Scope() boundary")

    def get_bounds(self, rows):
        """Get start and end line, which can be found in *rows*.

        Returns:
            start, end - tuple of start and end strings found in *rows*

        Raises:
            ValueError: no start/end line pairs was found in *rows*.

        """
        rows = list(rows)
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            if self._is_found(s, rows) and self._is_found(e, rows):
                return s, e
        msg = self._error_message(rows)
        raise ValueError(msg)

    @staticmethod
    def _is_found(line, rows):
        """
        Return:
           True, if *line* found at start of some entry in *rows*
           False otherwise
        """
        for r in rows:
            if r.startswith(line):
                return True
        return False

    def _error_message(self, rows):
        """Prepare error message with diagnostics.

        Returns:
            string with message text
        """
        msg = []
        msg.append("start or end line markers not found in *rows*")
        for marker in self.__markers:
            s = marker['start']
            e = marker['end']
            msg.append("is_found: {} <{}>".format(self._is_found(s, rows), s))
            msg.append("is_found: {} <{}>".format(self._is_found(e, rows), e))
        return "\n".join(msg)

    def __repr__(self):  # possible misuse of special method consider using __str__
        s = self.__markers[0]['start'][:10]
        e = self.__markers[0]['end'][:10]
        return "bound by start <{}...> and end <{}...>".format(s, e)

# FIXME: not refactoring above, refactroing code below


class ParsingCommand():
    def __init__(self, varhead, headers, required_units):
        """Create parsing instructions for an individual variable.

        Args:
            varhead (str):
                varaible name, ex: 'GDP'
            headers (str or list of strings):
                header string(s) associated with variable names
                ex: "Oбъем ВВП" or ["Oбъем ВВП", "Индекс физического объема произведенного ВВП"]
            required_units (str or list):
                required units of measurement for *varhead*,
                ex: 'bln_usd' or ['rog', 'rub']
        """
        self.varhead = varhead
        self._header_strings = as_list(headers)
        self._required_units = as_list(required_units)

    @property
    def mapper(self):
        return {hs: self.varhead for hs in self._header_strings}

    @property
    def required(self):
        return list(make_label(self.varhead, unit)
                    for unit in self._required_units)

    @property
    def units(self):
        return self._required_units


class Def(object):
    """Holds together:
        - parsing commands
        - (optional) defintion scope
        - (optional) custom reader function name

       Properties:
           - mapper (dict)
           - required (list)
           - units (dict)
           FIXME: is it a fucntion name or fucn itself?
            - reader (str)

       Public method:
            - get_bounds()

    """

    def __init__(self, commands, scope=None, func_name=None, units=UNITS):
        self.commands = as_list(commands)
        self.scope = self._get_scope(scope)
        self.reader = self._get_reader(func_name)
        self.units = units

    def _get_scope(self, sc):
        """
        Raises:
            TypeError: if *sc* is not Scope().
        """
        if sc is None:
            return None
        if isinstance(sc, Scope):
            self.scope = sc
        else:
            raise TypeError(sc)

    def _get_reader(self, func_name: str):
        """
        Raises:
            KeyError: if *funcname* is not valid.
        """
        if func_name is None:
            return None
        try:
            return FUNC_MAPPER[func_name]
        except KeyError:
            raise KeyError(f'<{func_name}> not available')

    @property
    def mapper(self):
        d = {}
        for c in self.commands:
            d.update(c.mapper)
        return d

    @property
    def required(self):
        return [r for c in self.commands for r in c.required]

    def get_bounds(self, rows):
        return self.scope.get_bounds(rows)

# descriptions


descriptions = dict(GDP="Валовый внутренний продукт (ВВП)")

# parsing definition

PARSING_DEFINITION = {'default': None, 'segments': []}
_commands = [
    ParsingCommand(varhead="GDP",
                   headers = ["Oбъем ВВП",
                              "Индекс физического объема произведенного ВВП, в %",
                              "Валовой внутренний продукт"],
                   required_units = ["bln_rub", "yoy"]),
    ParsingCommand("INDPRO",
                   "Индекс промышленного производства",
                   ["yoy", "rog"]),
    ParsingCommand("UNEMPL", 
                   ["Уровень безработицы", "Общая численность безработных"],
                   "pct"),
    ParsingCommand("WAGE_NOMINAL", 
                   ["Среднемесячная номинальная начисленная заработная плата работников организаций",
                    "Среднемесячная номинальная начисленная заработная плата одного работника"],
                    "rub"), 
    ParsingCommand("WAGE_REAL", 
                   ["Реальная начисленная заработная плата работников организаций",
                    "Реальная начисленная заработная плата одного работника"],
                    ["yoy", "rog"]), 
    ParsingCommand("TRANSPORT_FREIGHT",
                   "Коммерческий грузооборот транспорта",
                   "bln_tkm"),
]
PARSING_DEFINITION['default'] = Def(commands=_commands) 

# step 2 - segment definitions
sc = Scope("1.9. Внешнеторговый оборот – всего",
           "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
sc.add_bounds("1.10. Внешнеторговый оборот – всего",
              "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
sc.add_bounds("1.10. Внешнеторговый оборот – всего",
              "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья")
pc = [
    ParsingCommand("EXPORT_GOODS",
                   ["экспорт товаров – всего",
                    "Экспорт товаров"],
                   "bln_usd"),
    ParsingCommand("IMPORT_GOODS",
                   ["импорт товаров – всего",
                    "Импорт товаров"],
                   "bln_usd")
]
PARSING_DEFINITION['segments'].append(Def(pc, sc))


sc = Scope("1.6. Инвестиции в основной капитал",
           "1.6.1. Инвестиции в основной капитал организаций")
sc.add_bounds("1.7. Инвестиции в основной капитал",
              "1.7.1. Инвестиции в основной капитал организаций")
pc = ParsingCommand("INVESTMENT",
                    "Инвестиции в основной капитал",
                    ["bln_rub", "yoy", "rog"])
PARSING_DEFINITION['segments'].append(Def(pc, sc))


## TODO: PPI
# add here

# FIXME: must post to api/desc
#         desc="Индекс потребительских цен (ИПЦ)")
#         desc="ИПЦ (непродтовары)")
#         "ИПЦ (продтовары)")
#         "ИПЦ (услуги)")
#         "ИПЦ (алкоголь)")

## -- CPI
sc = Scope(start="3.5. Индекс потребительских цен",
           end="4. Социальная сфера")
pc = [
    ParsingCommand("CPI",
                   "Индекс потребительских цен",
                   "rog"),
    ParsingCommand("CPI_NONFOOD",
                   ["непродовольственные товары",
                    "непродовольст- венные товары"],
                   "rog"),
    ParsingCommand("CPI_FOOD",
                   "продукты питания",
                   "rog"),
    ParsingCommand("CPI_SERVICES",
                   "услуги",
                   "rog"),
    ParsingCommand("CPI_ALCOHOL",
                   "алкогольные напитки",
                   "rog"),
]
PARSING_DEFINITION['segments'].append(Def(pc, sc))


sc = Scope("1.12. Оборот розничной торговли",
           "1.12.1. Оборот общественного питания")
sc.add_bounds("1.13. Оборот розничной торговли",
              "1.13.1. Оборот общественного питания")
pc = [
    ParsingCommand("RETAIL_SALES",
                   "Оборот розничной торговли",
                   ["bln_rub", "yoy", "rog"]),
    ParsingCommand("RETAIL_SALES_FOOD",
                   ["продовольственные товары",
                    "пищевые продукты, включая напитки и табачные изделия",
                    "пищевые продукты, включая напитки, и табачные изделия"],
                   ["bln_rub", "yoy", "rog"]),
    ParsingCommand("RETAIL_SALES_NONFOOD",
                   "непродовольственные товары",
                   ["bln_rub", "yoy", "rog"])
]
PARSING_DEFINITION['segments'].append(Def(pc, sc))


sc = Scope("2.1.1. Доходы (по данным Федерального казначейства)",
           "2.1.2. Расходы (по данным Федерального казначейства)")
pc = [
    ParsingCommand(
        "GOV_REVENUE_ACCUM_CONSOLIDATED",
        "Консолидированный бюджет",
        "bln_rub"),
    ParsingCommand(
        "GOV_REVENUE_ACCUM_FEDERAL",
        "Федеральный бюджет",
        "bln_rub"),
    ParsingCommand(
        "GOV_REVENUE_ACCUM_SUBFEDERAL",
        "Консолидированные бюджеты субъектов Российской Федерации",
        "bln_rub")]
PARSING_DEFINITION['segments'].append(Def(pc, sc, 'fiscal'))

sc = Scope("2.1.2. Расходы (по данным Федерального казначейства)",
           "2.1.3. Превышение доходов над расходами")

pc = [
    ParsingCommand(
        "GOV_EXPENSE_ACCUM_CONSOLIDATED",
        "Консолидированный бюджет",
        "bln_rub"),
    ParsingCommand(
        "GOV_EXPENSE_ACCUM_FEDERAL",
        "Федеральный бюджет",
        "bln_rub"),
    ParsingCommand(
        "GOV_EXPENSE_ACCUM_SUBFEDERAL",
        "Консолидированные бюджеты субъектов Российской Федерации",
        "bln_rub")]
PARSING_DEFINITION['segments'].append(Def(pc, sc, 'fiscal'))


sc = Scope("2.1.3. Превышение доходов над расходами",
           "2.2. Сальдированный финансовый результат")
pc = [
    ParsingCommand(
        "GOV_SURPLUS_ACCUM_FEDERAL",
        "Федеральный бюджет",
        "bln_rub"),
    ParsingCommand(
        "GOV_SURPLUS_ACCUM_SUBFEDERAL",
        "Консолидированные бюджеты субъектов Российской Федерации",
        "bln_rub")]
PARSING_DEFINITION['segments'].append(Def(pc, sc, 'fiscal'))

# TODO: add more definitons
