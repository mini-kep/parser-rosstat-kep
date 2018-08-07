from copy import copy
from profilehooks import profile

from kep.util import iterate
from kep.dates import date_span
from kep.parser.reader import get_tables
from kep.parser.units import get_mapper
from locations import interim_csv, unit_mapper

ALL_DATES = date_span('2009-04', '2018-06')
       

def expected_labels(name, units):
    return [(name, unit) for unit in units]

def labels(tables):
    return [(t.name, t.unit) for t in tables] 

def assert_labels_found(tables, name, units):
    parsed_tables = [t for t in tables if t]
    current_labels = labels(parsed_tables) 
    for lab in expected_labels(name, units):
        if lab not in current_labels:
            raise AssertionError(lab)
        
def common_parse(tables, name, headers, units, **kwargs):
    parse_headers(tables, name, headers)
    trail_down_names(tables, name, units)
    assert_labels_found(tables, name, units)
    assert expected_labels

    
def parse_units(tables, base_mapper):
    for t in tables:
        for header in t.headers:
            unit = base_mapper.extract(header)
            if unit:
                t.unit = unit
    
def parse_headers(tables, name, headers):
    headers = iterate(headers)
    for t in tables:
        if t.contains_any(headers):
            t.name = name
            break

def trail_down_names(tables, name, units):
    """Assign trailing variable names in tables.

      We look for a case where a table name is defined once and there are
      following tables with expected unit names, but no variable name
      specified. In this case we assign table name similar to previous table.
    """
    _units = copy(units)
    trailing_allowed = False
    for i, table in enumerate(tables):
        if not _units:
            break
        if table.name == name:
            trailing_allowed = True
            if table.unit in _units:
                # unit already found, exclude it from futher search
                _units.remove(table.unit)
        if (i > 0 and
            trailing_allowed and
            table.name is None and
            table.unit in _units):
            # then
            table.name = tables[i - 1].name
            _units.remove(table.unit)

def parsed(tables):
    return [t for t in tables if t]

def select(tables, name):
    return [t for t in tables if t.name==name]

#@profile(immediate=True, entries=0)
def main(parsing_parameters):
    base_mapper = get_mapper(unit_mapper())            
    for year, month in ALL_DATES:
        print(year, month)
        path = interim_csv(year, month)
        tables = get_tables(path)
        parse_units(tables, base_mapper)        
        for p in parsing_parameters:
            common_parse(tables, **p)
    return parsed(tables)        


groups = ('BUSINESS_ACTIVITY', ('GDP', 'INDPRO', 'DWELL'))
parsing_parameters = [
    dict(name='GDP', 
         units=['bln_rub', 'yoy'], 
         headers=['Валовой внутренний продукт',
                  'Объем валового внутреннего продукта', 
                  'Объем ВВП']),
    dict(name='INDPRO', 
         units=['yoy', 'rog' , 'ytd'], 
         headers=['Индекс промышленного производства']),    
    dict(name='DWELL',
         units=['mln_m2'],
         headers=['Ввод в действие жилых домов',
                  'Ввод в действие жилых домов организациями всех форм собственности']),
     
         
    ]  
tables = main(parsing_parameters) 

# read json +  bakc to groups what we are looking for

"""
[
    {
        "header": [
            "Oбъем ВВП",
            "Индекс физического объема произведенного ВВП, в %",
            "Валовой внутренний продукт"
        ],
        "unit": [
            "bln_rub",
            "yoy"
        ],
        "var": "GDP"
    },
    {
        "header": "Индекс промышленного производства",
        "unit": [
            "yoy",
            "rog"
        ],
        "var": "INDPRO"
    },
    {
        "header": [
            "Индекс производства продукции сельского хозяйства в хозяйствах всех категорий",
            "Продукция сельского хозяйства в хозяйствах всех категорий"
        ],
        "unit": "yoy",
        "var": "AGROPROD"
    },
    {
        "header": [
            "Среднемесячная номинальная начисленная заработная плата работников организаций",
            "Среднемесячная номинальная начисленная заработная плата одного работника"
        ],
        "unit": "rub",
        "var": "WAGE_NOMINAL"
    },
    {
        "header": [
            "Реальная начисленная заработная плата работников организаций",
            "Реальная начисленная заработная плата одного работника"
        ],
        "unit": [
            "yoy",
            "rog"
        ],
        "var": "WAGE_REAL"
    },
    {
        "header": "Коммерческий грузооборот транспорта",
        "unit": "bln_tkm",
        "var": "TRANSPORT_FREIGHT"
    },
    {
        "header": [
            "Уровень безработицы",
            "Общая численность безработных"
        ],
        "unit": "pct",
        "var": "UNEMPL"
    },
    {
        "header": [
            "Индексы цен производителей промышленных товаров"
        ],
        "unit": "rog",
        "var": "PPI"
    }
]
    """







       