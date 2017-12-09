import re

NAMES = [
    "BRENT",
    "CPI_ALCOHOL_rog",
    "CPI_FOOD_rog",
    "CPI_NONFOOD_rog",
    "CPI_rog",
    "CPI_SERVICES_rog",
    "EXPORT_GOODS_bln_usd",
    "GDP_bln_rub",
    "GDP_yoy",
    "GOV_EXPENSE_CONSOLIDATED_bln_rub",
    "GOV_EXPENSE_FEDERAL_bln_rub",
    "GOV_EXPENSE_SUBFEDERAL_bln_rub",
    "GOV_REVENUE_CONSOLIDATED_bln_rub",
    "GOV_REVENUE_FEDERAL_bln_rub",
    "GOV_REVENUE_SUBFEDERAL_bln_rub",
    "GOV_SURPLUS_FEDERAL_bln_rub",
    "GOV_SURPLUS_SUBFEDERAL_bln_rub",
    "IMPORT_GOODS_bln_usd",
    "INDPRO_rog",
    "INDPRO_yoy",
    "INVESTMENT_bln_rub",
    "INVESTMENT_rog",
    "INVESTMENT_yoy",
    "RETAIL_SALES_bln_rub",
    "RETAIL_SALES_FOOD_bln_rub",
    "RETAIL_SALES_FOOD_rog",
    "RETAIL_SALES_FOOD_yoy",
    "RETAIL_SALES_NONFOOD_bln_rub",
    "RETAIL_SALES_NONFOOD_rog",
    "RETAIL_SALES_NONFOOD_yoy",
    "RETAIL_SALES_rog",
    "RETAIL_SALES_yoy",
    "TRANSPORT_FREIGHT_bln_tkm",
    "UNEMPL_pct",
    "USDRUR_CB",
    "UST_10YEAR",
    "UST_1MONTH",
    "UST_1YEAR",
    "UST_20YEAR",
    "UST_2YEAR",
    "UST_30YEAR",
    "UST_3MONTH",
    "UST_3YEAR",
    "UST_5YEAR",
    "UST_6MONTH",
    "UST_7YEAR",
    "WAGE_NOMINAL_rub",
    "WAGE_REAL_rog",
    "WAGE_REAL_yoy"
]

# part of issue https://github.com/mini-kep/db/blob/master/doc/listing.md
# https://github.com/mini-kep/db/blob/master/doc/listing.md

# setting

concepts = dict(labor=['WAGE_*', 'UNEMPL'],
                output=['IND*', 'TRANSPORT_FREIGHT'])


# TODO 1: make a selection function that produces a list of
#       variable names based on regex or variable head

#       use <https://github.com/mini-kep/parser-rosstat-kep/blob/master/src/csv2df/util_label.py>
#       to split labels

# TODO 2: write tests for the fucntion using the guidelines
#         <https://github.com/mini-kep/guidelines/blob/master/testing.md>


# 1. get_re() - это 'не вынести регекс в отдельную функцию'
#    make_regex() делает что-то полезное с законченной зоно ответственности
#    + ее можно тестировать
# 2. небольшой костыль был: 
#    search = search[:-1]
#    если что-то надо с хвоста отрезать - непрвильно объединение сделали

def make_regex(patterns):
    matched = []
    base_regex = re.compile('([A-Z]+_?)+')
    for p in patterns:
        match = base_regex.match(p)
        matched.append(match.group())
    return '|'.join(matched)

assert make_regex(['WAGE_*', 'UNEMPL']) == 'WAGE_|UNEMPL'    
    

def make_namelist(patterns, names=NAMES):
    namelist = []
    regex = re.compile(make_regex(patterns))
    for name in names:
        hit = regex.search(name)
        if hit:
            namelist.append(name)
    return namelist

# 3. теперь главный вопрос - зачем это делалось?
#    см. ниже
assert make_namelist(['WAGE_*'], ['UNNECESSARY_WAGE_1']) == [] 


labor = make_namelist(concepts['labor'])
assert set(labor) == set(["WAGE_NOMINAL_rub",
                          "WAGE_REAL_rog",
                          "WAGE_REAL_yoy",
                          "UNEMPL_pct"
                          ])