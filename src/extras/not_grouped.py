# what variables not grouped?
groups = {
    'GDP': [
        'GDP_bln_rub',
        'GDP_yoy'],
    'output': [
        'INDPRO_rog',
        'INDPRO_yoy',
        'AGROPROD_yoy',
        'TRANSPORT_FREIGHT_bln_tkm'],
    'prices': [
        'CPI_rog',
        'PPI_rog',
        'CPI_FOOD_rog',
        'CPI_NONFOOD_rog',
        'CPI_SERVICES_rog',
        'CPI_ALCOHOL_rog',
    ],
    'employment': ['UNEMPL_pct'],
    'wages': [
        'WAGE_NOMINAL_rub',
        'WAGE_REAL_rog',
        'WAGE_REAL_yoy'],
    'foreing trade': [
        'IMPORT_GOODS_bln_usd',
        'EXPORT_GOODS_bln_usd'],
    'budget': [
        'GOV_EXPENSE_CONSOLIDATED_bln_rub',
        'GOV_EXPENSE_FEDERAL_bln_rub',
        'GOV_EXPENSE_SUBFEDERAL_bln_rub',
        'GOV_REVENUE_CONSOLIDATED_bln_rub',
        'GOV_REVENUE_FEDERAL_bln_rub',
        'GOV_REVENUE_SUBFEDERAL_bln_rub',
        'GOV_SURPLUS_FEDERAL_bln_rub',
        'GOV_SURPLUS_SUBFEDERAL_bln_rub'],
    'investment': [
        'INVESTMENT_bln_rub',
        'INVESTMENT_rog',
        'INVESTMENT_yoy'],
    'retail sales': [
        'RETAIL_SALES_FOOD_bln_rub',
        'RETAIL_SALES_FOOD_rog',
        'RETAIL_SALES_FOOD_yoy',
        'RETAIL_SALES_NONFOOD_bln_rub',
        'RETAIL_SALES_NONFOOD_rog',
        'RETAIL_SALES_NONFOOD_yoy',
        'RETAIL_SALES_bln_rub',
        'RETAIL_SALES_rog',
        'RETAIL_SALES_yoy'],
    'corporate': [
        'CORP_RECEIVABLE_OVERDUE_bln_rub',
        'CORP_RECEIVABLE_bln_rub']}

# иначе не получается складывать объекты 'numpy.ndarray'. если разное
# кол-во элементов - ошибка.
all_vars = list(set(list(dfa.columns.values) +
                    list(dfq.columns.values) +
                    list(dfm.columns.values)))
x = [k for keys in groups.values() for k in keys]
not_found = [y for y in all_vars if y not in x]
print('Variables not grouped:\n', not_found)
