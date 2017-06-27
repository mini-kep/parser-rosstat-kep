# -*- coding: utf-8 -*-
import pytest
import copy

import parse
import files
import splitter


def test_get_date_funcs_return_pd_Timestamps():
    import pandas as pd
    from datetime import date
    assert parse.get_date_month_end(2015, 8) == pd.Timestamp('2015-08-31 00:00:00')
    assert parse.get_date_quarter_end(2015, 1) == pd.Timestamp('2015-03-31 00:00:00')
    assert parse.get_date_quarter_end(2015, 4) == pd.Timestamp('2015-12-31 00:00:00')
    assert parse.get_date_year_end(2015) == pd.Timestamp('2015-12-31 00:00:00')
    # shorter, pandas-native functions
    assert parse.get_date_month_end(2015, 1) == \
           pd.Timestamp(date(2015, 1, 1)) + pd.offsets.MonthEnd()
    assert parse.get_date_quarter_end(2015, 4) == \
           pd.Timestamp(date(2015, 4*3, 1)) + pd.offsets.QuarterEnd()
    assert parse.get_date_year_end(2015) == \
           pd.Timestamp(str(2015)) + pd.offsets.YearEnd()


# TESTING END TO END
year, month = 2017, 4
vint = parse.Vintage(2017, 4)
# break csv to tables with variable names
tables = vint.tables
# emit values from tables
dpoints = vint.dpoints
# convert stream values to pandas dataframes
frame = vint.frames


def test_Datapoints_is_included_annual_1999_values_in_2017_4():
    test_datapoints = [{'freq': 'm', 'label': 'EXPORT_GOODS_TOTAL_bln_usd', 'month': 1, 'value': 4.5, 'year': 1999},
{'freq': 'a', 'label': 'EXPORT_GOODS_TOTAL_bln_usd', 'value': 75.6, 'year': 1999},
{'freq': 'a', 'label': 'EXPORT_GOODS_TOTAL_yoy', 'value': 101.5, 'year': 1999},
{'freq': 'a', 'label': 'IMPORT_GOODS_TOTAL_bln_usd', 'value': 39.5, 'year': 1999},
{'freq': 'a', 'label': 'IMPORT_GOODS_TOTAL_yoy', 'value': 68.1, 'year': 1999},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub', 'value': 1213.6, 'year': 1999},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_FEDERAL_bln_rub', 'value': 615.5, 'year': 1999},
{'freq': 'a', 'label': 'GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub', 'value': 660.8, 'year': 1999},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub', 'value': 1258.0, 'year': 1999},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_FEDERAL_bln_rub', 'value': 666.9, 'year': 1999},
{'freq': 'a', 'label': 'GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub', 'value': 653.8, 'year': 1999},
{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_FEDERAL_bln_rub', 'value': -51.4, 'year': 1999},
{'freq': 'a', 'label': 'GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub', 'value': 7.0, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_bln_rub', 'value': 1797.4, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_yoy', 'value': 94.2, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_FOOD_bln_rub', 'value': 866.1, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_FOOD_yoy', 'value': 93.6, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_NONFOODS_bln_rub', 'value': 931.3, 'year': 1999},
{'freq': 'a', 'label': 'RETAIL_SALES_NONFOODS_yoy', 'value': 94.7, 'year': 1999},
{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
{'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999}]
    for x in test_datapoints:
        assert dpoints.is_included(x)


def test_dfa_in_2017_4():
    assert frame.dfa['1999'].transpose().__str__() == \
"""time_index                              1999-12-31
label                                             
year                                        1999.0
EXPORT_GOODS_TOTAL_bln_usd                    75.6
EXPORT_GOODS_TOTAL_yoy                       101.5
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
IMPORT_GOODS_TOTAL_yoy                        68.1
IND_PROD_yoy                                   NaN
RETAIL_SALES_FOOD_bln_rub                    866.1
RETAIL_SALES_FOOD_yoy                         93.6
RETAIL_SALES_NONFOODS_bln_rub                931.3
RETAIL_SALES_NONFOODS_yoy                     94.7
RETAIL_SALES_bln_rub                        1797.4
RETAIL_SALES_yoy                              94.2"""


def test_dfq_in_2017_4():
    assert frame.dfq.loc["2017-03", ].transpose().__str__() == """time_index                              2017-03-31
label                                             
year                                        2017.0
qtr                                            1.0
EXPORT_GOODS_TOTAL_bln_usd                    82.2
EXPORT_GOODS_TOTAL_rog                        99.5
EXPORT_GOODS_TOTAL_yoy                       136.0
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
IMPORT_GOODS_TOTAL_rog                        86.8
IMPORT_GOODS_TOTAL_yoy                       125.9
IND_PROD_rog                                  83.1
IND_PROD_yoy                                 100.1
RETAIL_SALES_FOOD_bln_rub                   3275.3
RETAIL_SALES_FOOD_rog                         83.4
RETAIL_SALES_FOOD_yoy                         97.0
RETAIL_SALES_NONFOODS_bln_rub               3460.1
RETAIL_SALES_NONFOODS_rog                     82.2
RETAIL_SALES_NONFOODS_yoy                     99.3
RETAIL_SALES_bln_rub                        6735.4
RETAIL_SALES_rog                              82.8
RETAIL_SALES_yoy                              98.2"""


def test_dfm_in_2017_4():
    assert frame.dfm.loc["2017-01", ].transpose().__str__() == """time_index                              2017-01-31
label                                             
year                                        2017.0
month                                          1.0
EXPORT_GOODS_TOTAL_bln_usd                    25.1
EXPORT_GOODS_TOTAL_rog                        80.3
EXPORT_GOODS_TOTAL_yoy                       146.6
GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub      1682.9
GOV_EXPENSE_ACCUM_FEDERAL_bln_rub           1230.5
GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub         452.2
GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub      1978.8
GOV_REVENUE_ACCUM_FEDERAL_bln_rub           1266.0
GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub         493.7
GOV_SURPLUS_ACCUM_FEDERAL_bln_rub             35.5
GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub          41.5
IMPORT_GOODS_TOTAL_bln_usd                    13.7
IMPORT_GOODS_TOTAL_rog                        70.2
IMPORT_GOODS_TOTAL_yoy                       138.8
IND_PROD_rog                                  76.2
IND_PROD_yoy                                 102.3
IND_PROD_ytd                                 102.3
RETAIL_SALES_FOOD_bln_rub                   1073.8
RETAIL_SALES_FOOD_rog                         75.2
RETAIL_SALES_FOOD_yoy                         96.6
RETAIL_SALES_NONFOODS_bln_rub               1133.7
RETAIL_SALES_NONFOODS_rog                     75.0
RETAIL_SALES_NONFOODS_yoy                     98.7
RETAIL_SALES_bln_rub                        2207.5
RETAIL_SALES_rog                              75.1
RETAIL_SALES_yoy                              97.7"""


def test_Datapoints_get():
    testpoints_1999a = [{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
                        {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999}]
    assert list(dpoints.get("a", "GDP", 1999)) == testpoints_1999a


def test_end_to_end_latest_month():
    vintage = parse.Vintage(year=None, month=None)
    vintage.validate()


# TESTING INDIVIDUAL FUNCTIONS
def test_labels_funcs():
    assert parse.extract_unit("GDP_mln_rub") == "mln_rub"
    assert parse.extract_varname("GDP_mln_rub") == "GDP"
    assert parse.split_label("GDP_mln_rub") == ("GDP", "mln_rub")
    assert parse.make_label("GDP", "mln_rub") == "GDP_mln_rub"


def test_Header():
    assert parse.Header.KNOWN != parse.Header.UNKNOWN


def test_RowHolder_is_matched():
    foo = parse.RowStack.is_matched
    assert foo(pat="Объем ВВП", textline="Объем ВВП текущего года") is True
    assert foo(pat="Объем ВВП", textline="1.1 Объем ВВП") is False


def test_to_float():
    for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
        assert parse.to_float(x) is False
    assert parse.to_float('5.678,') == 5.678
    assert parse.to_float('5.678,,') == 5.678
    assert parse.to_float("5.6") == 5.6
    assert parse.to_float("5,6") == 5.6
    assert parse.to_float("5,67") == 5.67
    assert parse.to_float("5,67,") == 5.67
    assert parse.to_float('123,0 4561)') == 123
    assert parse.to_float('6762,31)2)') == 6762.3
    assert parse.to_float('1734.4 1788.42)') == 1734.4


def test_get_year():
    assert parse.get_year("19991)") == 1999
    assert parse.get_year("1999") == 1999
    assert parse.get_year("1812") is None


def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=parse.ENC)
    assert "\0" not in z

header_row = parse.Row(['Объем ВВП', ''])
data_row = parse.Row(['1991', '10', '20', '30', '40'])

TABLE = parse.Table(headers=[header_row],
                    datarows=[data_row])
TABLE.header.varname = 'GDP'
TABLE.header.unit = 'rog'


def test_Table_str():
    assert TABLE.__repr__() == 'Table GDP_rog (1 headers, 1 datarows)'


def test_Table_repr():
    assert TABLE.__str__() == """Table for variable GDP_rog
Number of columns: 4
varname: GDP, unit: rog
- <Объем ВВП>
------------------
1991 | 10 20 30 40
------------------"""


def test_Table_is_defined():
    # table has label, but misses splitter_func specified
    assert TABLE.is_defined() is False

    # table has both label and splitter_func
    table = copy.deepcopy(TABLE)
    table.splitter_func = splitter.SPECIAL_FUNC_NAMES_TO_FUNC_MAPPER['fiscal']
    assert table.is_defined() is True

    # test tables from "TESTING END TO END" section
    for table in tables:
        assert table.is_defined() is True


def all_values():
    # emit all values for debugging to_float()
    csv_path = files.get_path_csv()
    for table in parse.Tables(csv_path).get_all():
        for row in table.datarows:
            for value in row.data:
                yield value


def all_heads():
    # emit all heads for debugging get_year()
    csv_path = files.get_path_csv()
    csv_dicts = parse.read_csv(csv_path)
    for d in csv_dicts:
        yield d.name

if __name__ == "__main__":
    pytest.main()
