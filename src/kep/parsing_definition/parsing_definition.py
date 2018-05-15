"""Parsing definition to identify tables in the data source file.
    
   A defnition contains a list of nested dicts. 

   Each dict has following keys: 
   - commands, a list of dicts each with following keys:     
       - variable name ('GDP')
       - corresponding headers ('Oбъем ВВП')
       - units of measurement ('bln_rub')
   - boundaries (start and end lines of text)   
   - reader function name(string)

"""

from kep.csv2df.util.label import make_label

COMMANDS_DEFAULT = [dict(
    var='GDP',
    header=['Oбъем ВВП',
            'Индекс физического объема произведенного ВВП, в %',
            'Валовой внутренний продукт'],
    unit=['bln_rub', 'yoy']),
    dict(
    var='INDPRO',
    header='Индекс промышленного производства',
    unit=['yoy', 'rog']),
    dict(
    var='AGROPROD',
    header=['Индекс производства продукции сельского хозяйства в хозяйствах всех категорий',
            'Продукция сельского хозяйства в хозяйствах всех категорий'],
    unit='yoy'),
    dict(
    var='WAGE_NOMINAL',
    header=['Среднемесячная номинальная начисленная заработная плата работников организаций',
            'Среднемесячная номинальная начисленная заработная плата одного работника'],
    unit='rub'),
    dict(
    var='WAGE_REAL',
    header=['Реальная начисленная заработная плата работников организаций',
            'Реальная начисленная заработная плата одного работника'],
    unit=['yoy', 'rog']),
    dict(
    var='TRANSPORT_FREIGHT',
    header='Коммерческий грузооборот транспорта',
    unit='bln_tkm'),
    dict(
    var='UNEMPL',
    header=['Уровень безработицы', 'Общая численность безработных'],
    unit='pct'),
    dict(
    var='PPI',
    header=['Индексы цен производителей промышленных товаров'],
    unit='rog'),
]

COMMANDS_BY_SEGMENT = [
    dict(
        boundaries=[
            dict(start='1.9. Внешнеторговый оборот – всего',
                 end='1.9.1. Внешнеторговый оборот со странами дальнего зарубежья'),
            dict(start='1.10. Внешнеторговый оборот – всего',
                 end='1.10.1. Внешнеторговый оборот со странами дальнего зарубежья'),
            dict(start='1.10. Внешнеторговый оборот – всего',
                 end='1.10.1.Внешнеторговый оборот со странами дальнего зарубежья')],
        commands=[
            dict(
                var='EXPORT_GOODS',
                header=['экспорт товаров – всего', 'Экспорт товаров'],
                unit='bln_usd'),
            dict(
                var='IMPORT_GOODS',
                header=['импорт товаров – всего',
                        'Импорт товаров'],
                unit='bln_usd')]
    ),
    dict(
        boundaries=[
            dict(start='1.6. Инвестиции в основной капитал',
                 end='1.6.1. Инвестиции в основной капитал организаций'),
            dict(start='1.7. Инвестиции в основной капитал',
                 end='1.7.1. Инвестиции в основной капитал организаций')],
        commands=[
            dict(
                var='INVESTMENT',
                header=['Инвестиции в основной капитал'],
                unit=['bln_rub', 'yoy', 'rog'])]
    ),
    dict(
        boundaries=[
            dict(start='3.5. Индекс потребительских цен',
                 end='4. Социальная сфера')],
        commands=[
            dict(
                var='CPI',
                header='Индекс потребительских цен',
                unit='rog'),
            dict(
                var='CPI_NONFOOD',
                header=['непродовольственные товары',
                        'непродовольст- венные товары'],
                unit='rog'),
            dict(
                var='CPI_FOOD',
                header='продукты питания',
                unit='rog'),
            dict(
                var='CPI_SERVICES',
                header='услуги',
                unit='rog'),
            dict(
                var='CPI_ALCOHOL',
                header='алкогольные напитки',
                unit='rog')]
    ),
    dict(
        boundaries=[
            dict(start='1.12. Оборот розничной торговли',
                 end='1.12.1. Оборот общественного питания'),
            dict(start='1.13. Оборот розничной торговли',
                 end='1.13.1. Оборот общественного питания')],
        commands=[
            dict(var='RETAIL_SALES',
                 header='Оборот розничной торговли',
                 unit=['bln_rub', 'yoy', 'rog']),
            dict(var='RETAIL_SALES_FOOD',
                 header=['продовольственные товары',
                         'пищевые продукты, включая напитки и табачные изделия',
                         'пищевые продукты, включая напитки, и табачные изделия'],
                 unit=['bln_rub', 'yoy', 'rog']),
            dict(var='RETAIL_SALES_NONFOOD',
                 header='непродовольственные товары',
                 unit=['bln_rub', 'yoy', 'rog'])
        ]
    ),
    dict(
        boundaries=[
            dict(start='2.1.1. Доходы (по данным Федерального казначейства)',
                 end='2.1.2. Расходы (по данным Федерального казначейства)')],
        commands=[
            dict(var='GOV_REVENUE_ACCUM_CONSOLIDATED',
                 header='Консолидированный бюджет',
                 unit='bln_rub'),
            dict(var='GOV_REVENUE_ACCUM_FEDERAL',
                 header='Федеральный бюджет',
                 unit='bln_rub'),
            dict(var='GOV_REVENUE_ACCUM_SUBFEDERAL',
                 header='Консолидированные бюджеты субъектов Российской Федерации',
                 unit='bln_rub')],
        reader='fiscal'
    ),
    dict(
        boundaries=[
            dict(start='2.1.2. Расходы (по данным Федерального казначейства)',
                 end='2.1.3. Превышение доходов над расходами')],
        commands=[
            dict(var='GOV_EXPENSE_ACCUM_CONSOLIDATED',
                 header='Консолидированный бюджет',
                 unit='bln_rub'),
            dict(var='GOV_EXPENSE_ACCUM_FEDERAL',
                 header='Федеральный бюджет',
                 unit='bln_rub'),
            dict(var='GOV_EXPENSE_ACCUM_SUBFEDERAL',
                 header='Консолидированные бюджеты субъектов Российской Федерации',
                 unit='bln_rub')],
        reader='fiscal'
    ),
    dict(
        boundaries=[
            dict(start='2.1.3. Превышение доходов над расходами',
                 end='2.2. Сальдированный финансовый результат')],
        commands=[
            dict(var='GOV_SURPLUS_ACCUM_FEDERAL',
                 header='Федеральный бюджет',
                 unit='bln_rub'),
            dict(var='GOV_SURPLUS_ACCUM_SUBFEDERAL',
                 header='Консолидированные бюджеты субъектов Российской Федерации',
                 unit='bln_rub')],
        reader='fiscal'
    ),
    dict(
        # no quarterly or annual data for this definition
        boundaries=[
            dict(start='2.4.2. Дебиторская задолженность',
                 end='2.5. Просроченная задолженность по заработной плате на начало месяца')],
        commands=[
            dict(var='CORP_RECEIVABLE',
                 header='Дебиторская задолженность',
                 unit='bln_rub'),
            dict(var='CORP_RECEIVABLE_OVERDUE',
                 header='в том числе просроченная',
                 unit='bln_rub'
                 )]
    )
]


from typing import List, Union, Any
StringType = Union[str, List[str]]


def as_list(x: Any):
    """Transform *x* to list *[x]*.

       Returns:
           list
    """
    if isinstance(x, list):
        return x
    elif isinstance(x, tuple):
        return list(x)
    else:
        return [x]


def make_parsing_command(var: str, header: StringType, unit: StringType):
    """Create parsing instructions for an individual variable.

    Keys:
        varname (str):
            varaible name, ex: 'GDP'
        table_headers-strings (list of strings):
            header string(s) associated with variable names
            ex: ['Oбъем ВВП'] or ['Oбъем ВВП', 'Индекс физического объема произведенного ВВП']
        units (list of strings):
            required_labels unit(s) of measurement
            ex: ['bln_usd]' or ['rog', 'rub']
    """
    return dict(varname = var,
                table_headers = as_list(header), 
                required_units = as_list(unit))


def make_definition_entry(commands: List[dict] , 
                          # FIXME: is this type annotation valid?
                          boundaries: List[dict] = [], 
                          reader: str = ''):
    commands_list = [make_parsing_command(**c) for c in as_list(commands)]
    return dict(commands = commands_list,
                boundaries = boundaries,
                reader = reader)    


def make_parsing_definition_list(default=COMMANDS_DEFAULT,
                                 by_segment=COMMANDS_BY_SEGMENT):
    definitions = [make_definition_entry(default)]
    for segment_dict in by_segment:
        pdef = make_definition_entry(**segment_dict)        
        definitions.append(pdef)
    return definitions


PARSING_DEFINITIONS = make_parsing_definition_list()
assert isinstance(PARSING_DEFINITIONS, list)
assert isinstance(PARSING_DEFINITIONS[0], dict)
assert isinstance(PARSING_DEFINITIONS[1], dict)
assert PARSING_DEFINITIONS[0]['boundaries'] == []
assert PARSING_DEFINITIONS[1]['boundaries'] != []


from schema import Schema

DEFINITIONS_SCHEMA = Schema(
          [{'commands': [{'varname': str, 
                          'table_headers': [str], 
                          'required_units': [str]}], 
            'boundaries': [{'start': str, 'end': str}], 
            'reader': str}]
)
    
def validate_defintion_list(defs, schema=DEFINITIONS_SCHEMA):
    schema.validate(defs)     

validate_defintion_list(PARSING_DEFINITIONS)
    

d1 =  [{'commands': [{'table_headers': ['экспорт товаров – всего', 'Экспорт товаров'],
                      'required_units': ['bln_usd'],
                      'varname': 'EXPORT_GOODS'},
                     {'table_headers': ['импорт товаров – всего', 'Импорт товаров'],
                      'required_units': ['bln_usd'],
                      'varname': 'IMPORT_GOODS'}], 
        'boundaries': [{'end': '1.9.1. Внешнеторговый оборот со странами дальнего зарубежья',
                        'start': '1.9. Внешнеторговый оборот – всего'},
                       {'end': '1.10.1. Внешнеторговый оборот со странами дальнего зарубежья',
                        'start': '1.10. Внешнеторговый оборот – всего'},
                       {'end': '1.10.1.Внешнеторговый оборот со странами дальнего зарубежья',
                        'start': '1.10. Внешнеторговый оборот – всего'}], 
        'reader': 'fiscal'}]

DEFINITIONS_SCHEMA.validate(d1)


def make_super_definition_entry(commands: List[dict] , 
                          boundaries: List[dict] = [], 
                          reader: str = ''):
    # preprocessing
    commands_list = [make_parsing_command(**c) for c in as_list(commands)]
    # control tructure
    return dict(mapper = make_table_header_mapper(commands_list),
                required_labels = make_required_labels(commands_list),
                boundaries = boundaries,
                reader = reader)  


def make_table_header_mapper(commands):
    result = {}
    for c in commands:
        for header in c['table_headers']:
            result[header] = c['varname'] 
    return result

    
def make_required_labels(commands):
    result = []
    for c in commands:
        for unit in c['required_units']:
            result.append(make_label(c['varname'], unit))
    return result

def make_super_parsing_definition_list(default=COMMANDS_DEFAULT,
                                       by_segment=COMMANDS_BY_SEGMENT,
                                       factory=make_super_definition_entry):
    definitions = [factory(default)]
    for segment_dict in by_segment:
        pdef = factory(**segment_dict)        
        definitions.append(pdef)
    return definitions

DL = make_super_parsing_definition_list()


# WARNING: this is optional part, this serialisation is never used
import json
import pathlib


from ruamel.yaml import YAML
#import sys
from pathlib import Path

p = Path("out.yaml")

yaml=YAML(typ='rt')
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.default_style="'"
yaml.indent(mapping=2, sequence=4, offset=2)
#yaml.dump_all(PARSING_DEFINITIONS, sys.stdout)


def dump(what, filename):
    x = json.dumps(what, ensure_ascii=False, sort_keys=True, indent=4)
    pathlib.Path(filename).write_text(x)


def read(filname):
    return json.loads(pathlib.Path(filname).read_text())


if __name__ == '__main__': # pragma: no cover
    dump(PARSING_DEFINITIONS, 'parsing_definitions.json')
