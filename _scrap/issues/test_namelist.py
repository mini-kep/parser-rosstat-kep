import pytest


from namelist import make_namelist


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


class Test_make_namelist():
    def test_make_namelist_on_asterisk_returns_expected_list_of_strings(self):
        result = make_namelist(patterns=['WAGE_*'], names=NAMES) 
        assert result == ['WAGE_NOMINAL_rub', 'WAGE_REAL_rog', 'WAGE_REAL_yoy']
    
    def test_make_namelist_returns_sorted_list(self):
        names = ['WAGE_Z', 'WAGE_A']
        result = make_namelist(patterns=['WAGE_*'], names=names) 
        assert result == ['WAGE_A', 'WAGE_Z']
        
    def test_make_namelist_on_string_returns_expected_list_of_names(self):
        result = make_namelist(patterns=['UNEMPL'], names=NAMES) 
        assert result == ['UNEMPL_pct']
    
    def test_make_namelist_misses_name_in_the_middle(self):
        result = make_namelist(patterns=['WAGE_*'], names=['UNNECESSARY_WAGE_1']) 
        assert result == []
    
    def test_make_namelist_misses_missing_string(self):
        result = make_namelist(patterns="ABC", names=['DEF', 'XYZ'])
        assert result == []
    
    def test_make_namelist_ignores_lowercase_pattern(self):
        result = make_namelist(patterns="def", names=['DEF', 'XYZ'])
        assert result == []    
    
    def test_make_namelist_ignores_lowercase_name(self):
        result = make_namelist(patterns="def", names=['def', 'XYZ'])
        assert result == []     
    
if __name__ == '__main__':
    pytest.main([__file__])    
    
    
    
    