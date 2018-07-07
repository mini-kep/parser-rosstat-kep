import kep

def read_dataframes(csv_path: str):
    values = kep.to_values(csv_path, kep.UNITS, kep.NAMERS)
    return kep.unpack_dataframes(values)
    
if __name__ == '__main__':
    from paths import PATH_CSV 
    tables = kep.parsed_tables(PATH_CSV, kep.UNITS, kep.NAMERS)
    dfa, dfq, dfm = read_dataframes(PATH_CSV)
    
  
r = ['2018', '', '101,9', '', '', '', '102,9', '101,5', '101,0', '101,3', '', '', '', '', '', '', '', '']
f=kep.row.get_format(len(r))
a = list(kep.row.emit_datapoints(r, 'INDPRO_yoy', f))
# wrong parsing in 2018
"""    
                                            2018-12-31
year                                            2018.0
AGROPROD_yoy                                       NaN
CPI_ALCOHOL_rog                                    NaN
CPI_FOOD_rog                                       NaN
CPI_NONFOOD_rog                                    NaN
CPI_SERVICES_mln                                   NaN
CPI_SERVICES_rog                                   NaN
DWELLINGS_CONSTRUCTION_mln_m2                      NaN
DWELLINGS_CONSTRUCTION_yoy                         NaN
EXPORT_GOODS_bln_usd                               NaN
EXPORT_GOODS_yoy                                   NaN
GDP_REAL_yoy                                     101.3
GDP_bln_rub                                        NaN
IMPORT_GOODS_bln_usd                               NaN
INDPRO_rog                                        97.8
INDPRO_yoy                                       101.1
INVESTMENT_BUDGET_FUNDS_FEDERAL_bln_rub            NaN
INVESTMENT_BUDGET_FUNDS_SUBFEDERAL_bln_rub         NaN
INVESTMENT_BUDGET_FUNDS_SUBFEDERAL_yoy             NaN
INVESTMENT_BUDGET_FUNDS_bln_rub                    NaN
INVESTMENT_EXTERNAL_FUNDS_bln_rub                  NaN
INVESTMENT_OWN_FUNDS_bln_rub                       NaN
INVESTMENT_bln_rub                                 NaN
INVESTMENT_yoy                                     NaN
PPI_mln_rub                                        NaN
PPI_rog                                            NaN
RETAIL_SALES_FOOD_bln_rub                          NaN
RETAIL_SALES_NONFOOD_bln_rub                       NaN
RETAIL_SALES_bln_rub                               NaN
TRANSPORT_FREIGHT_COMMERCIAL_bln_tkm               NaN
TRANSPORT_FREIGHT_COMMERCIAL_yoy                   NaN
TRANSPORT_FREIGHT_TOTAL_bln_tkm                    NaN
TRANSPORT_FREIGHT_TOTAL_yoy                        NaN
TRANSPORT_LOADING_RAIL_mln_t                       NaN
TRANSPORT_LOADING_RAIL_yoy                         NaN
UNEMPL_COUNT_mln                                   NaN
WAGE_REAL_yoy                                      NaN
WAGE_rub                                           NaN
""" 
    

# WIP:
#  - full new defintion of parsing_defintion.py
#  - convert to tests

# TODO - OTHER:
# - code review
# - run over many csv files: tab.csv and tab_old.csv + alldata/interim files

# WONTFIX:
#  - datapoint checks
#  - checking dataframes
#  - saving to disk
#  - clean notebook folders
#  - check a defintion against file (no duplicate values) - Namer.inspect()
#  - header found more than once in tables
#  - duplicate PPI_mln_rub
#  - special 12m - a  situation
#  - 1.7. Объем работ по виду деятельности ""Строительство - requires supress_apos()
#  - more definitions

# DONE
#  - type conversions and comment cleaning
#  - assert schema on namer imports
#  - write expected values
#  - timeit