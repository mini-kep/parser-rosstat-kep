# ----------------------------------------------------------------------------------------
#
# TODO - coverage of resulting frames by checkpoints 
# https://github.com/mini-kep/parser-rosstat-kep/issues/151
# 
# Setting (specification - dataframes - checkpoints):
#
# - specification has requited labals for parsing, it is guaranteed that parsing results ('dataframes')
#   have this set of labels 
# - Validate(year, month).dfs has three dataframes with parsing results ('dataframes')
# - we check them with checkpoints.validate() function using CHECKPOINTS datapoints

# How CHECKPOINTS are constructed?
#  -  a checkpoint is basically a frequency-label--date-value dictionary
#  -  there are several ways to define uch dictionaries, most explcicit is just a hardcoded constant
#     (in fact that was tried in some branches of repo)
#  -  we need a lot of chekpoints and some rather visual way of editing them
#  -  given this the checkpoints.CHECKPOINTS are constructued manually just using a printout (repr) of dataframes 
#     while this may not be the best way to construct a checkpoint, it is rather verbose.
#  -  the problem I see is that the variables that do not have a 1999 value, which start observationlater (eg INDPRO, PPI, some others)
#  -  another problem is that we just copy an occasional parsing result to CHEKCPOINTS, not really looking at CSV file 
#     is it is really the value in original data source

# Risks:
# - dataframes may have parsing results not covered by checkpoints
# - not all indicators start in 1999, they need other checkpoints 
# - checkpoints not strictly related to interim CSV values
# - we employ just one control datapoint per time series to ensure data interity, may not be enough to stay sure

# Immediate tasks:
#  - are all columns in dataframes covered by CHECKPOINTS? (uncovered time series / columns names) - moe important
#  - what are values in CHECKPOINTS that are not in dataframes? (unused checkpoints) - less important


# ----------------------------------------------------------------------------------------
#
# Related issues:
#  - how many variables are parsed, how many time sseries are there is the dataset in total, by ferequncy
#  - should speciifation include control datapoints?#
#
# ----------------------------------------------------------------------------------------
from collections import namedtuple

ANNUAL_STR = """
year                                1999.0
AGROPROD_yoy                         103.8
CPI_ALCOHOL_rog                      143.2
CPI_FOOD_rog                         135.0
CPI_NONFOOD_rog                      139.2
CPI_SERVICES_rog                     134.0
CPI_rog                              136.5
EXPORT_GOODS_bln_usd                  75.6
GDP_bln_rub                         4823.0
GDP_yoy                              106.4
GOV_EXPENSE_CONSOLIDATED_bln_rub    1258.0
GOV_EXPENSE_FEDERAL_bln_rub          666.9
GOV_EXPENSE_SUBFEDERAL_bln_rub       653.8
GOV_REVENUE_CONSOLIDATED_bln_rub    1213.6
GOV_REVENUE_FEDERAL_bln_rub          615.5
GOV_REVENUE_SUBFEDERAL_bln_rub       660.8
GOV_SURPLUS_FEDERAL_bln_rub          -51.4
GOV_SURPLUS_SUBFEDERAL_bln_rub         7.0
IMPORT_GOODS_bln_usd                  39.5
INVESTMENT_bln_rub                   670.4
INVESTMENT_yoy                       105.3
RETAIL_SALES_FOOD_bln_rub            866.1
RETAIL_SALES_FOOD_yoy                 93.6
RETAIL_SALES_NONFOOD_bln_rub         931.3
RETAIL_SALES_NONFOOD_yoy              94.7
RETAIL_SALES_bln_rub                1797.4
RETAIL_SALES_yoy                      94.2
TRANSPORT_FREIGHT_bln_tkm           3372.0
UNEMPL_pct                            13.0
WAGE_NOMINAL_rub                    1523.0
WAGE_REAL_yoy                         78.0
INDPRO_yoy                             NaN
PPI_rog                                NaN
"""

ANNUAL_STR_2016 = """
year                                2016.0
INDPRO_yoy                           101.3
PPI_rog                              107.5
"""

QTR_STR = """
year                                1999.0
qtr                                    1.0
AGROPROD_yoy                          97.2
CPI_ALCOHOL_rog                      118.2
CPI_FOOD_rog                         118.4
CPI_NONFOOD_rog                      114.0
CPI_SERVICES_rog                     109.5
CPI_rog                              116.0
EXPORT_GOODS_bln_usd                  15.3
GDP_bln_rub                          901.0
GDP_yoy                               98.1
GOV_EXPENSE_CONSOLIDATED_bln_rub     189.0
GOV_EXPENSE_FEDERAL_bln_rub          108.3
GOV_EXPENSE_SUBFEDERAL_bln_rub        91.5
GOV_REVENUE_CONSOLIDATED_bln_rub     171.9
GOV_REVENUE_FEDERAL_bln_rub           89.1
GOV_REVENUE_SUBFEDERAL_bln_rub        93.6
GOV_SURPLUS_FEDERAL_bln_rub          -19.2
GOV_SURPLUS_SUBFEDERAL_bln_rub         2.1
IMPORT_GOODS_bln_usd                   9.1
INDPRO_rog                             NaN
INDPRO_yoy                             NaN
INVESTMENT_bln_rub                    96.8
INVESTMENT_rog                         NaN
INVESTMENT_yoy                        93.8
PPI_rog                                NaN
RETAIL_SALES_FOOD_bln_rub            186.8
RETAIL_SALES_FOOD_rog                 85.0
RETAIL_SALES_FOOD_yoy                 92.7
RETAIL_SALES_NONFOOD_bln_rub         192.2
RETAIL_SALES_NONFOOD_rog              90.7
RETAIL_SALES_NONFOOD_yoy              84.3
RETAIL_SALES_bln_rub                 379.0
RETAIL_SALES_rog                      88.0
RETAIL_SALES_yoy                      88.1
TRANSPORT_FREIGHT_bln_tkm            821.0
UNEMPL_pct                            14.3
WAGE_NOMINAL_rub                    1248.0
WAGE_REAL_rog                         80.9
WAGE_REAL_yoy                         60.7"""

MONTHLY_STR = """
year                                1999.0
month                                  1.0
AGROPROD_yoy                          96.5
CORP_RECEIVABLE_OVERDUE_bln_rub      772.0
CORP_RECEIVABLE_bln_rub             1550.6
CPI_ALCOHOL_rog                      109.7
CPI_FOOD_rog                         110.4
CPI_NONFOOD_rog                      106.2
CPI_SERVICES_rog                     104.1
CPI_rog                              108.4
EXPORT_GOODS_bln_usd                   4.5
GOV_EXPENSE_CONSOLIDATED_bln_rub      45.6
GOV_EXPENSE_FEDERAL_bln_rub           27.4
GOV_EXPENSE_SUBFEDERAL_bln_rub        22.7
GOV_REVENUE_CONSOLIDATED_bln_rub      49.0
GOV_REVENUE_FEDERAL_bln_rub           27.8
GOV_REVENUE_SUBFEDERAL_bln_rub        25.7
GOV_SURPLUS_FEDERAL_bln_rub            0.4
GOV_SURPLUS_SUBFEDERAL_bln_rub         3.0
IMPORT_GOODS_bln_usd                   2.7
INVESTMENT_bln_rub                    28.5
INVESTMENT_rog                        42.5
INVESTMENT_yoy                        92.2
RETAIL_SALES_FOOD_bln_rub             60.3
RETAIL_SALES_FOOD_rog                 82.5
RETAIL_SALES_FOOD_yoy                 90.3
RETAIL_SALES_NONFOOD_bln_rub          61.5
RETAIL_SALES_NONFOOD_rog              81.0
RETAIL_SALES_NONFOOD_yoy              79.0
RETAIL_SALES_bln_rub                 121.8
RETAIL_SALES_rog                      81.7
RETAIL_SALES_yoy                      84.0
TRANSPORT_FREIGHT_bln_tkm            277.7
UNEMPL_pct                            14.3
WAGE_NOMINAL_rub                    1167.0
WAGE_REAL_rog                         72.5
WAGE_REAL_yoy                         58.6
"""
from numpy import isnan


def from_year(year):
    return str(int(year))


def from_month(year, month):
    year, month = int(year), int(month)
    return f'{year}-{month}'


def from_qtr(year, qtr):
    month = qtr * 3
    return from_month(year, month)


def as_dict(s):
    result = {}
    for row in s.strip().split('\n'):
        d = [x for x in row.split(' ') if x]
        val = float(d[-1])
        if not isnan(val):
            result[d[0]] = val
    return result


def extract_date(d):
    # onkery: Using `get` instead of `pop` to avoid false
    # positives during validation.
    year = int(d.get('year'))
    if 'month' in d.keys():
        month = int(d.get('month'))
        return from_month(year, month)
    elif 'qtr' in d.keys():
        qtr = int(d.get('qtr'))
        return from_qtr(year, qtr)
    else:
        return from_year(year)


Checkpoint = namedtuple("Checkpoint", ["date", "name", "value"])


def as_checkpoints(text):
    d = as_dict(text)
    return [Checkpoint(date=extract_date(d),
                       name=name,
                       value=d[name]) for name in d.keys()]


CHECKPOINTS = dict(
    a=as_checkpoints(ANNUAL_STR),
    q=as_checkpoints(QTR_STR),
    m=as_checkpoints(MONTHLY_STR)
)


# onkery: Using stub values for now-absent optional checkpoints to
# avoid awkward calls outside.
OPTIONAL_CHECKPOINTS = dict(
    a=as_checkpoints(ANNUAL_STR_2016),
    q=[],
    m=[],
)


def is_found(df, d):
    """Return true if dictionary *d* value
       if found in dataframe *df*.
    """
    try:
        return df.loc[d.date, d.name].iloc[0] == d.value
    except KeyError:
        return False


def validate(df, checkpoints):
    """Validate dataframe *df* with list of dictionaries
       *checkpoints*.
    """
    missed = find_missed_checkpoints(df, checkpoints)
    if missed:
        raise ValueError(f"Required checkpoints not found in dataframe: {missed}")

    uncovered = find_uncovered_column_names(df, checkpoints)
    if uncovered:
        raise ValueError(f"Variables not covered by checkpoints: {uncovered}")


# FIXME: should accept default and optional checkpoints list
#        desired bahaviour is following:
#        at least default or optional datapoint must be found for every column in dataframe
#        suggested interface is

def validate2(df, default_checkpoints, optional_checkpoints):
    missed_required = find_missed_checkpoints(df, default_checkpoints)
    missed_optional = find_missed_checkpoints(df, optional_checkpoints)

    # ensure a variable in dataframe is covered by at least one checkpoint
    missed = missed_required.intersection(missed_optional)
    if missed:
        raise ValueError(f"Required checkpoints not found in dataframe: {missed}")

    uncovered_required = find_uncovered_column_names(df, default_checkpoints)
    uncovered_optional = find_uncovered_column_names(df, optional_checkpoints)

    uncovered = uncovered_required.intersection(uncovered_optional)

    if uncovered:
        raise ValueError(f"Variables not covered by checkpoints: {uncovered_required}")


def find_missed_checkpoints(df, checkpoints):
    """
    Returns checkpoints not found in dataframe *df*.

    Args:
        df (pandas dataframe): parsing result
        checkpoints: list of dictionaries

    Returns:
        subset of *checkpoints* not found in dataframe *df*
    """
    return {c for c in checkpoints if not is_found(df, c)}


def find_uncovered_column_names(df, checkpoints):
    """
    Returns column names in dataframe *df*
    that are not covered by *checkpoints*.

    Args:
        df (pandas dataframe): parsing result
        checkpoints: list of dictionaries
    Returns:
        set of column names not matched by *checkpoints*
    """
    checkpoint_column_names = {c.name for c in checkpoints}
    df_column_names = set(df.columns)
    return df_column_names.difference(checkpoint_column_names)
