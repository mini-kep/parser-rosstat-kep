# first element

DEFAULT_COMMANDS = [dict(
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

PARSING_DEFINITION_BY_SEGMENT = [
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
                 unit='bln_rub',
                 # LATER: incorporate a check value
                 check=('bln_rub', 'm', '2017-09', 2445.8)
                 )]
    )
]


import json
import pathlib

from kep.csv2df.specification import Specification
from kep.parsing_definition.units import UNITS


def dump(what, filename):
    x = json.dumps(what, ensure_ascii=False, sort_keys=True, indent=4)
    pathlib.Path(filename).write_text(x)


def read(filname):
    return json.loads(pathlib.Path(filname).read_text())


def make_parsing_definition(default=DEFAULT_COMMANDS,
                            by_segment=PARSING_DEFINITION_BY_SEGMENT,
                            units=UNITS):
    pdef = Specification(default, units)
    for seg in by_segment:
        pdef.append(**seg)
    return pdef


PARSING_DEFINITION = make_parsing_definition()


if __name__ == '__main__': # pragma: no cover
    dump(DEFAULT_COMMANDS, 'default.json')
    dump(PARSING_DEFINITION_BY_SEGMENT, 'by_segment.json')
