# -*- coding: utf-8 -*-
import pytest
import kep.vintage as vintage

# TESTING END TO END
year, month = 2017, 4
vint = vintage.Vintage(2017, 4)
# break csv to tables with variable names
tables = vint.tables
# convert stream values to pandas dataframes
frame = vint.frames
#dpoints = vintage.Datapoints(tables)


def test_Datapoints_get_annual_values_():
    testpoints_1999a = [{'freq': 'a',
                         'label': 'GDP_bln_rub',
                         'value': 4823.0,
                         'year': 1999},
                        {'freq': 'a',
                         'label': 'GDP_yoy',
                         'value': 106.4,
                         'year': 1999}]
    assert list(dpoints.get("a", "GDP", 1999)) == testpoints_1999a


def test_end_to_end_latest_month():
    vint1 = vintage.Vintage(year=None, month=None)
    vint1.validate()


def test_Datapoints_is_included_annual_1999_values_in_2017_4():
    test_datapoints = [{'freq': 'm', 'label': 'EXPORT_GOODS_bln_usd', 'month': 1, 'value': 4.5, 'year': 1999},
                       {'freq': 'a', 'label': 'EXPORT_GOODS_bln_usd',
                           'value': 75.6, 'year': 1999},
                       {'freq': 'a', 'label': 'IMPORT_GOODS_bln_usd',
                           'value': 39.5, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub', 'value': 1213.6, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_FEDERAL_bln_rub', 'value': 615.5, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub', 'value': 660.8, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub', 'value': 1258.0, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_FEDERAL_bln_rub', 'value': 666.9, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub', 'value': 653.8, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_FEDERAL_bln_rub', 'value': -51.4, 'year': 1999},
                       #{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub', 'value': 7.0, 'year': 1999},
                       #{'freq': 'a', 'label': 'RETAIL_SALES_bln_rub', 'value': 1797.4, 'year': 1999},
                       #{'freq': 'a', 'label': 'RETAIL_SALES_FOOD_bln_rub', 'value': 866.1, 'year': 1999},
                       #{'freq': 'a', 'label': 'RETAIL_SALES_NONFOOD_bln_rub', 'value': 931.3, 'year': 1999},
                       {'freq': 'a', 'label': 'GDP_bln_rub',
                           'value': 4823.0, 'year': 1999},
                       {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999}]
    for x in test_datapoints:
        assert dpoints.includes(x)


dfa = frame.dfa['1999'].transpose()


def test_dfa_in_2017_4():
    assert str(dfa) == \
        """                      1999-12-31
year                      1999.0
CPI_ALC_rog                143.2
CPI_FOOD_rog               135.0
CPI_NONFOOD_rog            139.2
CPI_SERVICES_rog           134.0
CPI_rog                    136.5
EXPORT_GOODS_bln_usd        75.6
GDP_bln_rub               4823.0
GDP_yoy                    106.4
IMPORT_GOODS_bln_usd        39.5
INDPRO_yoy                   NaN"""


dfq = frame.dfq.loc["2017-03", ].transpose()


def test_dfq_in_2017_4():
    assert str(dfq) == \
        """                      2017-03-31
year                      2017.0
qtr                          1.0
CPI_ALC_rog                101.4
CPI_FOOD_rog               101.2
CPI_NONFOOD_rog            100.9
CPI_SERVICES_rog           100.8
CPI_rog                    101.0
EXPORT_GOODS_bln_usd        82.2
GDP_bln_rub                  NaN
GDP_yoy                    100.5
IMPORT_GOODS_bln_usd        48.0
INDPRO_rog                  83.1
INDPRO_yoy                 100.1"""


dfm = frame.dfm.loc["2017-01", ].transpose()


def test_dfm_in_2017_4():
    assert str(dfm) == \
        """                      2017-01-31
year                      2017.0
month                        1.0
CPI_ALC_rog                100.5
CPI_FOOD_rog               100.9
CPI_NONFOOD_rog            100.5
CPI_SERVICES_rog           100.5
CPI_rog                    100.6
EXPORT_GOODS_bln_usd        25.1
IMPORT_GOODS_bln_usd        13.7
INDPRO_rog                  76.2
INDPRO_yoy                 102.3"""


if __name__ == "__main__":
    pytest.main([__file__])
