"""Constant with parsing commands:
  
    PARSING_DEFINITIONS

"""

from kep.csv2df.specification import Def

# descriptions

#TODO: extend descriptions
descriptions = dict(abbr='GDP', ru='Валовый внутренний продукт', en='')
 


ANNUAL = [
   ('GDP_bln_rub', 1999, 4823.0),
   ('GDP_yoy', 1999, 106.4), 
   ('AGROPROD_yoy', 1999, 103.8),
]

#ANNUAL = [
#   ('AGROPROD_yoy',                  103.8
#    'GDP_bln_rub',                  4823.0
#    'GDP_yoy',                       106.4
#    'TRANSPORT_FREIGHT_bln_tkm',    3372.0
#    'UNEMPL_pct',                     13.0
#    'WAGE_NOMINAL_rub',             1523.0
#    'WAGE_REAL_yoy',                  78.0



QTR = [('GDP_bln_rub', 1999, {4: 1447}),
       ('CPI_rog', 1999, {1: 116.0, 2: 107.3, 3: 105.6, 4: 103.9})
       ]
          
MONTHLY = [('CPI_rog', 1999, {1: 108.4, 6: 101.9, 12: 101.3}),
           ('EXPORT_GOODS_bln_usd', 1999, {12: 9.7}),
           ('IMPORT_GOODS_bln_usd', 1999, {12: 4.0})
           ]


# default definition - applies to all CSV file
default_commands = [
    dict(
        var='GDP',
        header=['Oбъем ВВП',
                'Индекс физического объема произведенного ВВП, в %',
                'Валовой внутренний продукт'],
        unit=['bln_rub', 'yoy']),
    dict(
        var='INDPRO',
        header='Индекс промышленного производства',
        unit= ['yoy', 'rog']),
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

PARSING_DEFINITIONS = [Def(default_commands)]

# segment definitions
boundaries = [
    dict(start='1.9. Внешнеторговый оборот – всего',
           end='1.9.1. Внешнеторговый оборот со странами дальнего зарубежья'),
    dict(start='1.10. Внешнеторговый оборот – всего',
           end='1.10.1. Внешнеторговый оборот со странами дальнего зарубежья'),
    dict(start='1.10. Внешнеторговый оборот – всего',
           end='1.10.1.Внешнеторговый оборот со странами дальнего зарубежья')]    
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
PARSING_DEFINITIONS.append(Def(commands, boundaries))

boundaries = [
    dict(start='1.6. Инвестиции в основной капитал',
           end='1.6.1. Инвестиции в основной капитал организаций'),
    dict(start='1.7. Инвестиции в основной капитал',
           end='1.7.1. Инвестиции в основной капитал организаций')]
commands=[
    dict(        
        var='INVESTMENT',
        header=['Инвестиции в основной капитал'],
        unit=['bln_rub', 'yoy', 'rog'])]    
PARSING_DEFINITIONS.append(Def(commands, boundaries))


boundaries = [
    dict(start='3.5. Индекс потребительских цен',
           end='4. Социальная сфера')]
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
        unit='rog'),
]
PARSING_DEFINITIONS.append(Def(commands, boundaries))

boundaries = [
    dict(start='1.12. Оборот розничной торговли',
           end='1.12.1. Оборот общественного питания'),
    dict(start='1.13. Оборот розничной торговли',
           end='1.13.1. Оборот общественного питания')]
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
PARSING_DEFINITIONS.append(Def(commands, boundaries))

boundaries = [
    dict(start='2.1.1. Доходы (по данным Федерального казначейства)',
           end='2.1.2. Расходы (по данным Федерального казначейства)')]
commands=[
    dict(var='GOV_REVENUE_ACCUM_CONSOLIDATED',
         header='Консолидированный бюджет',
         unit='bln_rub'),
    dict(var='GOV_REVENUE_ACCUM_FEDERAL',
         header='Федеральный бюджет',
         unit='bln_rub'),
    dict(var='GOV_REVENUE_ACCUM_SUBFEDERAL',
         header='Консолидированные бюджеты субъектов Российской Федерации',
         unit='bln_rub')]
PARSING_DEFINITIONS.append(Def(commands, boundaries, reader='fiscal'))    

boundaries = [
    dict(start='2.1.2. Расходы (по данным Федерального казначейства)',
           end='2.1.3. Превышение доходов над расходами')]
commands=[
    dict(var='GOV_EXPENSE_ACCUM_CONSOLIDATED',
         header='Консолидированный бюджет',
         unit='bln_rub'),
    dict(var='GOV_EXPENSE_ACCUM_FEDERAL',
         header='Федеральный бюджет',
         unit='bln_rub'),
    dict(var='GOV_EXPENSE_ACCUM_SUBFEDERAL',
         header='Консолидированные бюджеты субъектов Российской Федерации',
         unit='bln_rub')]
PARSING_DEFINITIONS.append(Def(commands, boundaries, reader='fiscal')) 

boundaries = [
    dict(start='2.1.3. Превышение доходов над расходами',
           end='2.2. Сальдированный финансовый результат')]
commands=[
    dict(var='GOV_SURPLUS_ACCUM_FEDERAL',
         header='Федеральный бюджет',
         unit='bln_rub'),
    dict(var='GOV_SURPLUS_ACCUM_SUBFEDERAL',
         header='Консолидированные бюджеты субъектов Российской Федерации',
         unit='bln_rub')]
PARSING_DEFINITIONS.append(Def(commands, boundaries, reader='fiscal'))

# no quarterly or annual data for this definition
boundaries = [
    dict(start='2.4.2. Дебиторская задолженность',
           end='2.5. Просроченная задолженность по заработной плате на начало месяца')]
commands=[
    dict(var='CORP_RECEIVABLE',
         header='Дебиторская задолженность',
         unit='bln_rub'),
    dict(var='CORP_RECEIVABLE_OVERDUE',
         header='в том числе просроченная',
         unit='bln_rub',
         # LATER: incorporate a check value    
         check = ('bln_rub', 'm', '2017-09',  2445.8)           
         )]
   
PARSING_DEFINITIONS.append(Def(commands, boundaries))

if __name__ == '__main__':
    from kep.extractor import Frame, Extractor
    
    
    ANNUAL = [
       dict(name='GDP_bln_rub', date='1999', value=4823.0),
       dict(name='GDP_yoy', date='1999', value=106.4), 
       dict(name='AGROPROD_yoy', date='1999', value=103.8),
       dict(name='ZZZ_abc', date='1999', value=-1),
    ]
    
    QTR = [
       dict(name='GDP_bln_rub', date='1999-12', value=1447),
       dict(name='ZZZ_rog', date='1999-12', value=116.0)
       ]
    
    #TODO: add some monthly values
    
    frame = Frame(2017, 10, Def(default_commands))
    
    a = frame.isin('a', ANNUAL)
    assert a == [True, True, True, False]
    
    q = frame.isin('q', QTR)
    assert q == [True, False] # CPI is not in default definition
    
    dfa = frame.annual()
    dfq = frame.quarterly()
    dfm = frame.monthly()
    
    # to be used in parsing debugging:
    
    text = """1. Сводные показатели / Aggregated indicators					
1.1. Валовой внутренний продукт1) / Gross domestic product1)					
Объем ВВП, млрд.рублей /GDP, bln rubles					
1999	4823	901	1102	1373	1447
Индекс физического объема произведенного ВВП, в % / Volume index of produced GDP, percent					
1999	106,4	98,1	103,1	111,4	112,0"""
    pdef = Def(default_commands[0])
    e = Extractor(text, pdef)
    print(e.tables[0])    
    
    # TODO: add above as test
    