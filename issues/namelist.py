import itertools
import fnmatch

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
    "WAGE_REAL_yoy",
    "ZZZ"]


def get_names():
    return NAMES

def extract_varname(label):
    words = label.split('_')
    return '_'.join(itertools.takewhile(lambda word: word.isupper(), words))

def is_matched(name, pat):
    varhead = extract_varname(name)
    return fnmatch.fnmatch(varhead, pat)

def make_namelist(patterns, names):
    namelist = [name for pat in patterns for name in names if is_matched(name, pat)]
    return sorted(namelist)

def find_orphans(patterns, names):
    found = make_namelist(patterns, names)
    return list(set(names) - set(found))

                
if __name__ == '__main__':     
    from collections import OrderedDict
    categories = OrderedDict(gdp=['GDP*'],
                      output=['IND*', 'TRANSPORT_FREIGHT'],
                      i=['INVESTMENT'],
                      xpi=['CPI*', 'PPI*'], 
                      retail=['RETAIL_SALES*'],
                      gov=['GOV*'],
                      labor=['WAGE_*', 'UNEMPL'],
                      bop=['EXPORT*', 'IMPORT*'],
                      fx=['USDRUR*'],
                      glob=['UST*', 'BRENT'])
    cat2names = {key:make_namelist(categories[key], NAMES) 
                 for key in categories.keys()}
    patterns = [pat for patterns in categories.values() for pat in patterns]
    orp =  find_orphans(patterns, NAMES)
    assert orp == ['ZZZ']

