from collections import OrderedDict 

# mapper dictionary to convert text in table headers to unit of measurement
UNITS = OrderedDict([  # 1. MONEY
    ('млрд.долларов', 'bln_usd'),
    ('млрд. долларов', 'bln_usd'),
    ('млрд, долларов', 'bln_usd'),
    ('млрд.рублей', 'bln_rub'),
    ('млрд. рублей', 'bln_rub'),
    ('млн.рублей', 'mln_rub'),
    ('рублей / rubles', 'rub'),
    ('рублей', 'rub'),
    # 2. RATES OF CHANGE
    ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
    ('в % к декабрю предыдущего года', 'ytd'),
    ('в % к прошлому периоду', 'rog'),
    ('в % к предыдущему месяцу', 'rog'),
    ('в % к предыдущему периоду', 'rog'),
    ('% к концу предыдущего периода', 'rog'),
    # IMPORTANT:
    # this...
    ('период с начала отчетного года в % к соответствующему периоду предыдущего года', 'ytd'),
    #       ... must precede this
    # because 'в % к предыдущему периоду' is found in 'период с начала отчетного года в % к соответствующему периоду предыдущего года'
    ('в % к соответствующему периоду предыдущего года', 'yoy'),
    ('в % к соответствующему месяцу предыдущего года', 'yoy'),
    ('отчетный месяц в % к предыдущему месяцу', 'rog'),
    ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
    ('период с начала отчетного года', 'ytd'),
    # 3. OTHER UNITS (keep below RATES OF CHANGE)
    ("в % к экономически активному населению", "pct"),
    ('%', 'pct'),
    ('в % к ВВП', 'gdp_percent'),
    ('млрд.тонно-км', 'bln_tkm'),
    ('млрд. тонно-км', 'bln_tkm'),
    ('млн.тонн', 'mln_t'),
    # 4. stub for CPI section
    ("продукты питания", 'rog'),
    ("алкогольные напитки", 'rog'),
    ("непродовольственные товары", 'rog'),
    ("непродовольст- венные товары", 'rog'),
    ("услуги", 'rog'),
    ('млн.кв.м', 'mln_m2'),
    ('млн. кв. м', 'mln_m2'),
    ('млн.человек', 'mln'),
    # 5. named headers
    ('собственные средства предприятий', 'bln_rub'),
    ('привлеченные средства', 'bln_rub'),    
    ('из них бюджетные средства', 'bln_rub'),
    ('из федерального бюджета', 'bln_rub'),
    ('из бюджетов субъектов Российской Федерации', 'bln_rub'),
])

# 'official' names of units used in project front
UNIT_NAMES = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'mln': 'млн',
              'rub': 'руб.',
              'rog': '% к пред. периоду',
              'yoy': '% год к году',
              'ytd': 'период с начала года',
              'pct': '%',
              'bln_tkm': 'млрд. тонно-км',
              'mln_m2': 'млн. кв.м',
              'mln_t': 'млн. т',
              }

# validation: all units in mapper dict have an 'offical' name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())

doc = """
- name: GDP
  headers:
    - Oбъем ВВП
    - Валовой внутренний продукт
  units:
    - bln_rub
    
- name: GDP_REAL
  headers:
    - Индекс физического объема произведенного ВВП, в %
  units:
    - yoy

- name: INDPRO
  headers: 
    - Индекс промышленного производства
  units:
    - yoy
    - rog
    - ytd

- name: AGROPROD
  headers:
    - Индекс производства продукции сельского хозяйства в хозяйствах всех категорий
    - Продукция сельского хозяйства в хозяйствах всех категорий
  units: 
    - yoy

- name: WAGE
  headers:
    - Среднемесячная номинальная начисленная заработная плата работников организаций
    - Среднемесячная номинальная начисленная заработная плата одного работника
  units: 
    - rub

- name: WAGE_REAL
  headers:
    - Реальная начисленная заработная плата работников организаций
    - Реальная начисленная заработная плата одного работника
  units:
    - yoy
    - rog

- name: TRANSPORT_FREIGHT_TOTAL
  headers: 
      - Грузооборот транспорта, включая коммерческий и некоммерческий грузооборот
  units: 
      - bln_tkm    
    
- name: TRANSPORT_FREIGHT_COMMERCIAL
  headers: 
      - Коммерческий грузооборот транспорта,
  units: 
      - bln_tkm

- name: TRANSPORT_LOADING_RAIL
  headers: 
      - Погрузка грузов на железнодорожном транспорте
  units: 
      - mln_t

- name: INVESTMENT
  headers:
     - "1.6. Инвестиции в основной капитал"
     - "1.7. Инвестиции в основной капитал"
  units:
     - bln_rub
     - yoy
     - rog

- name: INVESTMENT_OWN_FUNDS
  headers:
     - собственные средства предприятий
  units:
     - bln_rub
  
- name: INVESTMENT_EXTERNAL_FUNDS
  headers:
     - привлеченные средства
  units:
     - bln_rub  
 
- name: INVESTMENT_BUDGET_FUNDS
  headers:
     - из них бюджетные средства
  units:
     - bln_rub  
     
- name: INVESTMENT_BUDGET_FUNDS_FEDERAL
  headers:
     - из федерального бюджета
  units:
     - bln_rub  

- name: INVESTMENT_BUDGET_FUNDS_SUBFEDERAL
  headers:
     - из бюджетов субъектов Российской Федерации
  units:
     - bln_rub       
     
  
# TODO:  
# 1.7. Объем работ по виду деятельности ""Строительство     


- name: EXPORT_GOODS
  headers:
      - экспорт товаров – всего
      - Экспорт товаров
  units: 
      - bln_usd
  starts:
      - "1.9. Внешнеторговый оборот – всего"
      - "1.10. Внешнеторговый оборот – всего"
      - "1.10. Внешнеторговый оборот – всего"
  ends:
      - "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья"
      - "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья"
      - "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья"
      
- name: IMPORT_GOODS
  headers:
      - импорт товаров – всего
      - Импорт товаро
  units: 
      - bln_usd
  starts:
      - "1.9. Внешнеторговый оборот – всего"
      - "1.10. Внешнеторговый оборот – всего"
      - "1.10. Внешнеторговый оборот – всего"
  ends:
      - "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья"
      - "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья"
      - "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья"       


- name: DWELLINGS_CONSTRUCTION
  headers:
      - Ввод в действие жилых домов организациями всех форм собственности
      - Ввод в действие жилых домов организациями всех форм
  units: 
      - mln_m2
      
- name: UNEMPL_COUNT
  headers:
    - Уровень безработицы
    - Общая численность безработных в возрасте 15 лет и старше
  units:

    - mln

- name: PPI
  headers:
    - Индексы цен производителей промышленных товаров
  units:
    - rog
    
    
- name: RETAIL_SALES
  headers:
    - Оборот розничной торговли
  units:
    - bln_rub
    - yoy
    - rog

- name: RETAIL_SALES_FOOD
  starts:
    - "Из общего объема оборота розничной торговли:"
  ends:
    - Оборот общественного питания 
  headers:
    - продовольственные товары
    - пищевые продукты, включая напитки и табачные изделия
    - пищевые продукты, включая напитки, и табачные изделия
  units:
    - bln_rub
    - yoy
    - rog

- name: RETAIL_SALES_NONFOOD
  starts:
    - "Из общего объема оборота розничной торговли:"
  ends:
    - Оборот общественного питания 
  headers: 
    - непродовольственные товары
  units:
    - bln_rub
    - yoy
    - rog   

- name: CPI
  headers: 
   - Индекс потребительских цен
  units: 
   - rog

- name: CPI_NONFOOD
  starts: 
   - "3.5. Индекс потребительских цен"
  ends: 
   - "4. Социальная сфера"
  headers:
    - непродовольственные товары
    - непродовольст- венные товары
  units: 
    - rog
  
- name: CPI_FOOD
  starts: 
   - "3.5. Индекс потребительских цен"
  ends: 
   - "4. Социальная сфера"
  headers: 
   - продукты питания
  units: 
   - rog

- name: CPI_SERVICES
  starts: 
   - "3.5. Индекс потребительских цен"
  ends: 
   - "4. Социальная сфера"
  headers: 
   - услуги
  units: 
   - rog

- name: CPI_ALCOHOL
  starts: 
   - "3.5. Индекс потребительских цен"
  ends: 
   - "4. Социальная сфера"
  headers: 
   - алкогольные напитки
  units: 
   - rog    
    
    
    
"""
import yaml  
# docs at https://github.com/keleshev/schema
from schema import Schema, And, Use, Optional, SchemaMissingKeyError
from reader import Namer        

PARSING_DEFINTIONS = list(yaml.load(doc))

schema = Schema({'name': str,
                 'headers': [str],
                 'units': [str],
                 Optional('reader'): str,
                 Optional('starts'): [str],
                 Optional('ends'): [str]
          })

for p in PARSING_DEFINTIONS:
    try:
        schema.validate(p)
    except SchemaMissingKeyError:
        raise ValueError(p)
    
NAMERS = [Namer(x['name'], x['headers'], x['units'],
                x.get('starts'), x.get('ends'),  x.get('reader'))
          for x in yaml.load(doc)]    
    