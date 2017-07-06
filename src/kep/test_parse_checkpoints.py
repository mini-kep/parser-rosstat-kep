# -*- coding: utf-8 -*-
import pytest
import vintage

# TESTING END TO END
year, month = 2017, 4
vint = vintage.Vintage(2017, 4)
# break csv to tables with variable names
tables = vint.tables
# convert stream values to pandas dataframes
frame = vint.frames
dpoints = vintage.Datapoints(tables)

def test_Datapoints_get_annual_values_():
    testpoints_1999a = [{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
                        {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999}]
    assert list(dpoints.get("a", "GDP", 1999)) == testpoints_1999a


def test_end_to_end_latest_month():
    vint1 = vintage.Vintage(year=None, month=None)
    vint1.validate()
    


def test_Datapoints_is_included_annual_1999_values_in_2017_4():
    test_datapoints = [{'freq': 'm', 'label': 'EXPORT_GOODS_TOTAL_bln_usd', 'month': 1, 'value': 4.5, 'year': 1999},
{'freq': 'a', 'label': 'EXPORT_GOODS_TOTAL_bln_usd', 'value': 75.6, 'year': 1999},
{'freq': 'a', 'label': 'IMPORT_GOODS_TOTAL_bln_usd', 'value': 39.5, 'year': 1999},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub', 'value': 1213.6, 'year': 1999},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_FEDERAL_bln_rub', 'value': 615.5, 'year': 1999},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub', 'value': 660.8, 'year': 1999},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub', 'value': 1258.0, 'year': 1999},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_FEDERAL_bln_rub', 'value': 666.9, 'year': 1999},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub', 'value': 653.8, 'year': 1999},
{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_FEDERAL_bln_rub', 'value': -51.4, 'year': 1999},
{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub', 'value': 7.0, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_bln_rub', 'value': 1797.4, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_FOOD_bln_rub', 'value': 866.1, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_NONFOODS_bln_rub', 'value': 931.3, 'year': 1999},
{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
{'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999}]
    for x in test_datapoints:
        assert dpoints.includes(x)


def test_dfa_in_2017_4():
    assert frame.dfa['1999'].transpose().__str__() == \
"""time_index                              1999-12-31
label                                             
year                                        1999.0
EXPORT_GOODS_TOTAL_bln_usd                    75.6
GDP_bln_rub                                 4823.0
GDP_yoy                                      106.4
GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub      1258.0
GOV_EXPENSE_ACCUM_FEDERAL_bln_rub            666.9
GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub         653.8
GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub      1213.6
GOV_REVENUE_ACCUM_FEDERAL_bln_rub            615.5
GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub         660.8
GOV_SURPLUS_ACCUM_FEDERAL_bln_rub            -51.4
GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub           7.0
IMPORT_GOODS_TOTAL_bln_usd                    39.5
IND_PROD_yoy                                   NaN
RETAIL_SALES_FOOD_bln_rub                    866.1
RETAIL_SALES_NONFOODS_bln_rub                931.3
RETAIL_SALES_bln_rub                        1797.4"""


def test_dfq_in_2017_4():
    assert frame.dfq.loc["2017-03", ].transpose().__str__() == """time_index                              2017-03-31
label                                             
year                                        2017.0
qtr                                            1.0
EXPORT_GOODS_TOTAL_bln_usd                    82.2
GDP_bln_rub                                    NaN
GDP_yoy                                      100.5
GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub      6892.4
GOV_EXPENSE_ACCUM_FEDERAL_bln_rub           3825.5
GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub        1976.7
GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub      7036.6
GOV_REVENUE_ACCUM_FEDERAL_bln_rub           3633.3
GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub        2325.6
GOV_SURPLUS_ACCUM_FEDERAL_bln_rub           -192.2
GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub         348.9
IMPORT_GOODS_TOTAL_bln_usd                    48.0
IND_PROD_rog                                  83.1
IND_PROD_yoy                                 100.1
RETAIL_SALES_FOOD_bln_rub                   3275.3
RETAIL_SALES_NONFOODS_bln_rub               3460.1
RETAIL_SALES_bln_rub                        6735.4"""


def test_dfm_in_2017_4():
    assert frame.dfm.loc["2017-01", ].transpose().__str__() == """time_index                              2017-01-31
label                                             
year                                        2017.0
month                                          1.0
EXPORT_GOODS_TOTAL_bln_usd                    25.1
GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub      1682.9
GOV_EXPENSE_ACCUM_FEDERAL_bln_rub           1230.5
GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub         452.2
GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub      1978.8
GOV_REVENUE_ACCUM_FEDERAL_bln_rub           1266.0
GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub         493.7
GOV_SURPLUS_ACCUM_FEDERAL_bln_rub             35.5
GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub          41.5
IMPORT_GOODS_TOTAL_bln_usd                    13.7
IND_PROD_rog                                  76.2
IND_PROD_yoy                                 102.3
IND_PROD_ytd                                 102.3
RETAIL_SALES_FOOD_bln_rub                   1073.8
RETAIL_SALES_NONFOODS_bln_rub               1133.7
RETAIL_SALES_bln_rub                        2207.5"""

if __name__ == "__main__":
    pytest.main([__file__])