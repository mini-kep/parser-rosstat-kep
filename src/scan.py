from copy import copy

from kep.util import iterate, load_yaml
from kep.dates import date_span
from kep.parser.reader import get_tables as read_tables
from kep.parser.units import UnitMapper
from locations import interim_csv

ALL_DATES = date_span('2009-04', '2018-06')
       

def expected_labels(name, units):
    return [(name, unit) for unit in iterate(units)]

def labels(tables):
    return [(t.name, t.unit) for t in tables] 

def assert_labels_found(tables, name, units):
    current_labels = labels(parsed(tables)) 
    expected_label_list = expected_labels(name, units)
    for lab in expected_label_list:
        if lab not in current_labels:
            raise AssertionError(f'{lab} must be in {expected_label_list}')

def parse_after_units(tables, name, headers, units, **kwargs):
    parse_headers(tables, name, headers)
    trail_down_names(tables, name, units)
    assert_labels_found(tables, name, units)
    
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
    _units = copy(iterate(units))
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

def find(tables, string):
   for t in tables:
        if t.contains_any([string]):
            return t
    

def get_parsing_parameters(filepath):
    return [x for x in load_yaml(filepath) if 'name' in x.keys()]

def get_unit_mapper(filepath):
    return UnitMapper(load_yaml(filepath)[0])

def get_tables(year, month):
    path = interim_csv(year, month)
    return read_tables(path)

def parse(year, month, parsing_parameters, base_mapper):    
    tables = get_tables(year, month)
    parse_units(tables, base_mapper)        
    for p in parsing_parameters:
         parse_after_units(tables, **p)
    return tables     
    

def main(parsing_parameters, base_mapper):
    for year, month in ALL_DATES:
        print(year, month)
        parse(year, month, parsing_parameters, base_mapper)

groups = ('BUSINESS_ACTIVITY', ('GDP', 'INDPRO', 'DWELL'))

def test_1():
    parsing_parameters = get_parsing_parameters('instructions.yml')    
    base_mapper = get_unit_mapper('base_units.yml') 
    tables = get_tables(2009, 4)
    t = find(tables, 'Ввод в действие жилых домов организациями всех форм собственности')
    p = parsing_parameters[2]
    parse_units([t], BASE_MAPPER)
    parse_after_units([t], **p)
    assert t.name == 'DWELL'
    assert t.unit == 'mln_m2'    


if __name__ == '__main__':
    parsing_parameters = get_parsing_parameters('instructions.yml')    
    base_mapper = get_unit_mapper('base_units.yml')
    tables = main(parsing_parameters, base_mapper ) 

# read json +  bakc to groups 
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







       