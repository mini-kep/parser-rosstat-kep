# -*- coding: utf-8 -*-
import parse
import cfg
import pytest


# TESTING END TO END

csv_path = cfg.get_path_csv(2017, 4)  
# break csv to tables with variable names
tables = parse.get_all_valid_tables(csv_path)
# emit values from tables
dpoints = parse.Datapoints(tables)    
# convert stream values to pandas dataframes     
frame = parse.Frame(datapoints=dpoints)
# sample access - dataframes
dfa = frame.get_dfa()
dfq = frame.get_dfq()
dfm = frame.get_dfm() 

def test_Datapoints_is_included():
    test_datapoints = [            
        {'freq': 'm', 'label': 'EXPORT_GOODS_TOTAL__bln_usd', 'month': 1, 'value': 4.5, 'year': 1999}, 
        {'freq': 'a',
  'label': 'EXPORT_GOODS_TOTAL__bln_usd',
  'value': 75.6,
  'year': 1999},
 {'freq': 'a',
  'label': 'EXPORT_GOODS_TOTAL__yoy',
  'value': 101.5,
  'year': 1999},
 {'freq': 'a',
  'label': 'IMPORT_GOODS_TOTAL__bln_usd',
  'value': 39.5,
  'year': 1999},
 {'freq': 'a',
  'label': 'IMPORT_GOODS_TOTAL__yoy',
  'value': 68.1,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub',
  'value': 1213.6,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_REVENUE_ACCUM_FEDERAL__bln_rub',
  'value': 615.5,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub',
  'value': 660.8,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub',
  'value': 1258.0,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_EXPENSE_ACCUM_FEDERAL__bln_rub',
  'value': 666.9,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub',
  'value': 653.8,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_SURPLUS_ACCUM_FEDERAL__bln_rub',
  'value': -51.4,
  'year': 1999},
 {'freq': 'a',
  'label': 'GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub',
  'value': 7.0,
  'year': 1999},
 {'freq': 'a',
  'label': 'RETAIL_SALES__bln_rub',
  'value': 1797.4,
  'year': 1999},
 {'freq': 'a', 'label': 'RETAIL_SALES__yoy', 'value': 94.2, 'year': 1999},
 {'freq': 'a',
  'label': 'RETAIL_SALES_FOOD__bln_rub',
  'value': 866.1,
  'year': 1999},
 {'freq': 'a', 'label': 'RETAIL_SALES_FOOD__yoy', 'value': 93.6, 'year': 1999},
 {'freq': 'a',
  'label': 'RETAIL_SALES_NONFOODS__bln_rub',
  'value': 931.3,
  'year': 1999},
 {'freq': 'a',
  'label': 'RETAIL_SALES_NONFOODS__yoy',
  'value': 94.7,
  'year': 1999},
 {'freq': 'a', 'label': 'GDP__bln_rub', 'value': 4823.0, 'year': 1999},
 {'freq': 'a', 'label': 'GDP__yoy', 'value': 106.4, 'year': 1999}]

    for x in test_datapoints:
       assert dpoints.is_included(x)

def test_dfa():    
    assert dfa.loc[1999,].__str__() == """label
EXPORT_GOODS_TOTAL__bln_usd                  75.6
EXPORT_GOODS_TOTAL__yoy                     101.5
GDP__bln_rub                               4823.0
GDP__yoy                                    106.4
GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub    1258.0
GOV_EXPENSE_ACCUM_FEDERAL__bln_rub          666.9
GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub       653.8
GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub    1213.6
GOV_REVENUE_ACCUM_FEDERAL__bln_rub          615.5
GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub       660.8
GOV_SURPLUS_ACCUM_FEDERAL__bln_rub          -51.4
GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub         7.0
IMPORT_GOODS_TOTAL__bln_usd                  39.5
IMPORT_GOODS_TOTAL__yoy                      68.1
IND_PROD__yoy                                 NaN
RETAIL_SALES_FOOD__bln_rub                  866.1
RETAIL_SALES_FOOD__yoy                       93.6
RETAIL_SALES_NONFOODS__bln_rub              931.3
RETAIL_SALES_NONFOODS__yoy                   94.7
RETAIL_SALES__bln_rub                      1797.4
RETAIL_SALES__yoy                            94.2
Name: 1999, dtype: float64"""

def test_dfq():
    pass  

def test_dfm():    
    assert dfm.loc["2017-01",].transpose().__str__() == """time_index                               2017-01-31
label                                              
year                                         2017.0
month                                           1.0
EXPORT_GOODS_TOTAL__bln_usd                    25.1
EXPORT_GOODS_TOTAL__rog                        80.3
EXPORT_GOODS_TOTAL__yoy                       146.6
GOV_EXPENSE_ACCUM_CONSOLIDATED__bln_rub      1682.9
GOV_EXPENSE_ACCUM_FEDERAL__bln_rub           1230.5
GOV_EXPENSE_ACCUM_SUBFEDERAL__bln_rub         452.2
GOV_REVENUE_ACCUM_CONSOLIDATED__bln_rub      1978.8
GOV_REVENUE_ACCUM_FEDERAL__bln_rub           1266.0
GOV_REVENUE_ACCUM_SUBFEDERAL__bln_rub         493.7
GOV_SURPLUS_ACCUM_FEDERAL__bln_rub             35.5
GOV_SURPLUS_ACCUM_SUBFEDERAL__bln_rub          41.5
IMPORT_GOODS_TOTAL__bln_usd                    13.7
IMPORT_GOODS_TOTAL__rog                        70.2
IMPORT_GOODS_TOTAL__yoy                       138.8
IND_PROD__rog                                  76.2
IND_PROD__yoy                                 102.3
IND_PROD__ytd                                 102.3
RETAIL_SALES_FOOD__bln_rub                   1073.8
RETAIL_SALES_FOOD__rog                         75.2
RETAIL_SALES_FOOD__yoy                         96.6
RETAIL_SALES_NONFOODS__bln_rub               1133.7
RETAIL_SALES_NONFOODS__rog                     75.0
RETAIL_SALES_NONFOODS__yoy                     98.7
RETAIL_SALES__bln_rub                        2207.5
RETAIL_SALES__rog                              75.1
RETAIL_SALES__yoy                              97.7""" 

def test_Datapoints_get():
    testpoints_1999a = [{'freq': 'a', 'label': 'GDP__bln_rub', 'value': 4823.0, 'year': 1999},
                        {'freq': 'a', 'label': 'GDP__yoy', 'value': 106.4, 'year': 1999}] 
    assert list(dpoints.get("a", "GDP", 1999)) == testpoints_1999a
    

def test_end_to_end_latest_month():
    parse.approve_csv(year=None,month=None)

# TESTING INDIVIDUAL FUNCTIONS
def test_get_year():
    assert parse.get_year("19991)") == 1999
    
   
def test_csv_has_no_null_byte():     
    csv_path = cfg.get_path_csv(2015, 2) 
    z = csv_path.read_text(encoding = parse.ENC)    
    assert "\0" not in z    
    
if __name__ == "__main__":
    pytest.main()