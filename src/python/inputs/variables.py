YAML_DOC = """
commands:
  - var: GDP
    header:
      - Oбъем ВВП
      - Индекс физического объема произведенного ВВП, в %
      - Валовой внутренний продукт
    unit:
      - bln_rub
      - yoy
  - var: INDPRO
    header: Индекс промышленного производства
    unit:
      - yoy
      - rog
  - var: AGROPROD
    header:
      - Индекс производства продукции сельского хозяйства в хозяйствах всех категорий
      - Продукция сельского хозяйства в хозяйствах всех категорий
    unit: yoy
  - var: WAGE_NOMINAL
    header:
      - Среднемесячная номинальная начисленная заработная плата работников организаций
      - Среднемесячная номинальная начисленная заработная плата одного работника
    unit: rub
  - var: WAGE_REAL
    header:
      - Реальная начисленная заработная плата работников организаций
      - Реальная начисленная заработная плата одного работника
    unit:
      - yoy
      - rog
  - var: TRANSPORT_FREIGHT
    header: Коммерческий грузооборот транспорта
    unit: bln_tkm
  - var: UNEMPL
    header:
      - Уровень безработицы
      - Общая численность безработных
    unit:
      - pct
      - yoy
      - mln
  - var: PPI
    header:
      - Индексы цен производителей промышленных товаров
    unit: rog
  - var: DWELLINGS_CONSTRUCTION
    header:
        - Ввод в действие жилых домов организациями всех форм собственности
        - Ввод в действие жилых домов организациями всех форм
    unit: mln_m2
---
boundaries:
  - start: 2.2. Сальдированный финансовый результат
    end: Убыточные организации
commands:
  - var: PROFIT_MINING
    header: Добыча полезных ископаемых
    unit: mln_rub
  - var: PROFIT_MANUF
    header: Обрабатывающие производства
    unit: mln_rub
  - var: PROFIT_POWER_GAS_WATER
    header:
        - Обеспечение электрической энергией, газом и паром
        - Производство и распределение электроэнергии, газа и воды
    unit: mln_rub
  - var: PROFIT_CONSTR
    header: Строительство
    unit: mln_rub
  - var: PROFIT_CONSTR
    header: Строительство
    unit: mln_rub
  - var: PROFIT_TRANSPORT_STOR_COMM
    header:
        - Транспортировка и хранение
        - Транспорт и связь
    unit: mln_rub
---
boundaries:
  - start: 1.9. Внешнеторговый оборот – всего
    end: 1.9.1. Внешнеторговый оборот со странами дальнего зарубежья
  - start: 1.10. Внешнеторговый оборот – всего
    end: 1.10.1. Внешнеторговый оборот со странами дальнего зарубежья
  - start: 1.10. Внешнеторговый оборот – всего
    end: 1.10.1.Внешнеторговый оборот со странами дальнего зарубежья
commands:
  - var: EXPORT_GOODS
    header:
      - экспорт товаров – всего
      - Экспорт товаров
    unit: bln_usd
  - var: IMPORT_GOODS
    header:
      - импорт товаров – всего
      - Импорт товаро
    unit: bln_usd
---
boundaries:
  - start: 1.6. Инвестиции в основной капитал
    end: 1.6.1. Инвестиции в основной капитал организаций
  - start: 1.7. Инвестиции в основной капитал
    end: 1.7.1. Инвестиции в основной капитал организаций
commands:
  - var: INVESTMENT
    header:
      - Инвестиции в основной капитал
    unit:
      - bln_rub
      - yoy
      - rog
---
boundaries:
  - start: 3.5. Индекс потребительских цен
    end: 4. Социальная сфера
commands:
  - var: CPI
    header: Индекс потребительских цен
    unit: rog
  - var: CPI_NONFOOD
    header:
      - непродовольственные товары
      - непродовольст- венные товары
    unit: rog
  - var: CPI_FOOD
    header: продукты питания
    unit: rog
  - var: CPI_SERVICES
    header: услуги
    unit: rog
  - var: CPI_ALCOHOL
    header: алкогольные напитки
    unit: rog
---
boundaries:
  - start: 1.12. Оборот розничной торговли
    end: 1.12.1. Оборот общественного питания
  - start: 1.13. Оборот розничной торговли
    end: 1.13.1. Оборот общественного питания
commands:
  - var: RETAIL_SALES
    header: Оборот розничной торговли
    unit:
      - bln_rub
      - yoy
      - rog
  - var: RETAIL_SALES_FOOD
    header:
      - продовольственные товары
      - пищевые продукты, включая напитки и табачные изделия
      - пищевые продукты, включая напитки, и табачные изделия
    unit:
      - bln_rub
      - yoy
      - rog
  - var: RETAIL_SALES_NONFOOD
    header: непродовольственные товары
    unit:
      - bln_rub
      - yoy
      - rog
---
boundaries:
  - start: 2.1.1. Доходы (по данным Федерального казначейства)
    end: 2.1.2. Расходы (по данным Федерального казначейства)
commands:
  - var: GOV_REVENUE_ACCUM_CONSOLIDATED
    header: Консолидированный бюджет
    unit: bln_rub
  - var: GOV_REVENUE_ACCUM_FEDERAL
    header: Федеральный бюджет
    unit: bln_rub
  - var: GOV_REVENUE_ACCUM_SUBFEDERAL
    header: Консолидированные бюджеты субъектов Российской Федерации
    unit: bln_rub
reader: fiscal
---
boundaries:
  - start: 2.1.2. Расходы (по данным Федерального казначейства)
    end: 2.1.3. Превышение доходов над расходами
commands:
  - var: GOV_EXPENSE_ACCUM_CONSOLIDATED
    header: Консолидированный бюджет
    unit: bln_rub
  - var: GOV_EXPENSE_ACCUM_FEDERAL
    header: Федеральный бюджет
    unit: bln_rub
  - var: GOV_EXPENSE_ACCUM_SUBFEDERAL
    header: Консолидированные бюджеты субъектов Российской Федерации
    unit: bln_rub
reader: fiscal
---
boundaries:
  - start: 2.1.3. Превышение доходов над расходами
    end: Убыточные организации
commands:
  - var: GOV_SURPLUS_ACCUM_FEDERAL
    header: Федеральный бюджет
    unit: bln_rub
  - var: GOV_SURPLUS_ACCUM_SUBFEDERAL
    header: Консолидированные бюджеты субъектов Российской Федерации
    unit: bln_rub
reader: fiscal
---
boundaries:
  - start: 2.4.2. Дебиторская задолженность
    end: 2.5. Просроченная задолженность по заработной плате на начало месяца
commands:
  - var: CORP_RECEIVABLE
    header: Дебиторская задолженность
    unit: bln_rub
  - var: CORP_RECEIVABLE_OVERDUE
    header: в том числе просроченная
    unit: bln_rub
"""
import yaml
_ = list(yaml.load_all(YAML_DOC))
