"""Validate parsing result dataframe using checkpoints. 

'Dataframes':
 - parsing results ('dataframes') are guarnteed to have exactly same set of labels as parsing definition

'Checkpoints':
- these are dictionaries with reference values for variables at all frequencies 
- we employ a rather verbose way of contructing the, from dataframe printouts

'Validation rules':
- are all checkpoints found daatframes?
- are all columns in dataframes covered by CHECKPOINTS?

Risks: 
 - not all indicators start in 1999, they need other checkpoints 
 - checkpoints not strictly related to interim CSV values
 - we employ just one control datapoint per time series to ensure data interity, may not be enough 

# Related issues:
#  - how many variables are parsed, how many time series are there is the dataset in total, by frequency

"""

from collections import namedtuple
from numpy import isnan
import pandas as pd

# How CHECKPOINTS are constructed?
#  -  a checkpoint is  a frequency-label--date-value dictionary
#  -  there are several ways to define uch dictionaries, most explcicit is just a hardcoded constant
#     (in fact that was tried in some branches of repo)
#  -  we need a lot of chekpoints and some rather visual way of editing them
#  -  we use a printout (repr) of dataframes  while this may not be the best way to construct a checkpoint, it is rather verbose.
#  -  the problem I see is that the variables that do not have a 1999 value, which start observationlater (eg INDPRO, PPI, some others)
#  -  another problem is that we just copy an occasional parsing result to CHEKCPOINTS, not really looking at CSV file 

VALUES_ANNUAL_1999 = dict(date='1999', 
                       freq='a',
                       values=
 {'AGROPROD_yoy': 103.8,
 'CPI_ALCOHOL_rog': 143.2,
 'CPI_FOOD_rog': 135.0,
 'CPI_NONFOOD_rog': 139.2,
 'CPI_SERVICES_rog': 134.0,
 'CPI_rog': 136.5,
 'EXPORT_GOODS_bln_usd': 75.6,
 'GDP_bln_rub': 4823.0,
 'GDP_yoy': 106.4,
 'GOV_EXPENSE_CONSOLIDATED_bln_rub': 1258.0,
 'GOV_EXPENSE_FEDERAL_bln_rub': 666.9,
 'GOV_EXPENSE_SUBFEDERAL_bln_rub': 653.8,
 'GOV_REVENUE_CONSOLIDATED_bln_rub': 1213.6,
 'GOV_REVENUE_FEDERAL_bln_rub': 615.5,
 'GOV_REVENUE_SUBFEDERAL_bln_rub': 660.8,
 'GOV_SURPLUS_FEDERAL_bln_rub': -51.4,
 'GOV_SURPLUS_SUBFEDERAL_bln_rub': 7.0,
 'IMPORT_GOODS_bln_usd': 39.5,
 'INVESTMENT_bln_rub': 670.4,
 'INVESTMENT_yoy': 105.3,
 'RETAIL_SALES_FOOD_bln_rub': 866.1,
 'RETAIL_SALES_FOOD_yoy': 93.6,
 'RETAIL_SALES_NONFOOD_bln_rub': 931.3,
 'RETAIL_SALES_NONFOOD_yoy': 94.7,
 'RETAIL_SALES_bln_rub': 1797.4,
 'RETAIL_SALES_yoy': 94.2,
 'TRANSPORT_FREIGHT_bln_tkm': 3372.0,
 'UNEMPL_pct': 13.0,
 'WAGE_NOMINAL_rub': 1523.0,
 'WAGE_REAL_yoy': 78.0,
}
)


VALUES_ANNUAL_2017 = dict(date='1999', 
                          freq='a',
                          values=
 {'INDPRO_yoy': 101.0,
  'PPI_rog': 108.4}
)


VALUES_QTR_1999 = dict(date='1999-03', 
                       freq='q',
                       values=
{'AGROPROD_yoy': 97.2,
 'CPI_ALCOHOL_rog': 118.2,
 'CPI_FOOD_rog': 118.4,
 'CPI_NONFOOD_rog': 114.0,
 'CPI_SERVICES_rog': 109.5,
 'CPI_rog': 116.0,
 'EXPORT_GOODS_bln_usd': 15.3,
 'GDP_bln_rub': 901.0,
 'GDP_yoy': 98.1,
 'GOV_EXPENSE_CONSOLIDATED_bln_rub': 189.0,
 'GOV_EXPENSE_FEDERAL_bln_rub': 108.3,
 'GOV_EXPENSE_SUBFEDERAL_bln_rub': 91.5,
 'GOV_REVENUE_CONSOLIDATED_bln_rub': 171.9,
 'GOV_REVENUE_FEDERAL_bln_rub': 89.1,
 'GOV_REVENUE_SUBFEDERAL_bln_rub': 93.6,
 'GOV_SURPLUS_FEDERAL_bln_rub': -19.2,
 'GOV_SURPLUS_SUBFEDERAL_bln_rub': 2.1,
 'IMPORT_GOODS_bln_usd': 9.1,
 'INVESTMENT_bln_rub': 96.8,
 'INVESTMENT_yoy': 93.8,
 'RETAIL_SALES_FOOD_bln_rub': 186.8,
 'RETAIL_SALES_FOOD_rog': 85.0,
 'RETAIL_SALES_FOOD_yoy': 92.7,
 'RETAIL_SALES_NONFOOD_bln_rub': 192.2,
 'RETAIL_SALES_NONFOOD_rog': 90.7,
 'RETAIL_SALES_NONFOOD_yoy': 84.3,
 'RETAIL_SALES_bln_rub': 379.0,
 'RETAIL_SALES_rog': 88.0,
 'RETAIL_SALES_yoy': 88.1,
 'TRANSPORT_FREIGHT_bln_tkm': 821.0,
 'UNEMPL_pct': 14.3,
 'WAGE_NOMINAL_rub': 1248.0,
 'WAGE_REAL_rog': 80.9,
 'WAGE_REAL_yoy': 60.7,
})


VALUES_MONTHLY_1999 = dict(date='1999-01', 
                           freq='m',
                           values=
                           {'AGROPROD_yoy': 96.5,
 'CORP_RECEIVABLE_OVERDUE_bln_rub': 772.0,
 'CORP_RECEIVABLE_bln_rub': 1550.6,
 'CPI_ALCOHOL_rog': 109.7,
 'CPI_FOOD_rog': 110.4,
 'CPI_NONFOOD_rog': 106.2,
 'CPI_SERVICES_rog': 104.1,
 'CPI_rog': 108.4,
 'EXPORT_GOODS_bln_usd': 4.5,
 'GOV_EXPENSE_CONSOLIDATED_bln_rub': 45.6,
 'GOV_EXPENSE_FEDERAL_bln_rub': 27.4,
 'GOV_EXPENSE_SUBFEDERAL_bln_rub': 22.7,
 'GOV_REVENUE_CONSOLIDATED_bln_rub': 49.0,
 'GOV_REVENUE_FEDERAL_bln_rub': 27.8,
 'GOV_REVENUE_SUBFEDERAL_bln_rub': 25.7,
 'GOV_SURPLUS_FEDERAL_bln_rub': 0.4,
 'GOV_SURPLUS_SUBFEDERAL_bln_rub': 3.0,
 'IMPORT_GOODS_bln_usd': 2.7,
 #'INDPRO_rog': nan,
 #'INDPRO_yoy': nan,
 'INVESTMENT_bln_rub': 28.5,
 'INVESTMENT_rog': 42.5,
 'INVESTMENT_yoy': 92.2,
 #'PPI_rog': nan,
 'RETAIL_SALES_FOOD_bln_rub': 60.3,
 'RETAIL_SALES_FOOD_rog': 82.5,
 'RETAIL_SALES_FOOD_yoy': 90.3,
 'RETAIL_SALES_NONFOOD_bln_rub': 61.5,
 'RETAIL_SALES_NONFOOD_rog': 81.0,
 'RETAIL_SALES_NONFOOD_yoy': 79.0,
 'RETAIL_SALES_bln_rub': 121.8,
 'RETAIL_SALES_rog': 81.7,
 'RETAIL_SALES_yoy': 84.0,
 'TRANSPORT_FREIGHT_bln_tkm': 277.7,
 'UNEMPL_pct': 14.3,
 'WAGE_NOMINAL_rub': 1167.0,
 'WAGE_REAL_rog': 72.5,
 'WAGE_REAL_yoy': 58.6})
    
   
def serialise_checkpoint(cp: dict):
    for name, value in cp['values'].items():
        yield [cp['date'], name, value]


assert ['1999-01', 'AGROPROD_yoy', 96.5] == next(serialise_checkpoint(VALUES_MONTHLY_1999))


def is_found(df, date, name, value):
    """Return true if *date, name, value* found in dataframe *df*."""
    try:
        return df.loc[date, name].iloc[0] == value
    except KeyError:
        return False      


def items_not_found_in_dataframe(df, cp: dict):
    return [[cp['freq']] + args for args in serialise_checkpoint(cp) 
            if not is_found(df, *args)]


def comparison_allowed(df, date: str):
    return any([df.index >= pd.Timestamp(date) for x in df.index]) 


def checkpoint_passed(df, cp: dict):
    return not items_not_found_in_dataframe(df, cp)


def not_found_factory(checkpoint: dict):
    def not_found(dataframe):
        return items_not_found_in_dataframe(dataframe, checkpoint)
    return not_found


def not_found_factory_conditional(checkpoint: dict, start_date: str):
    def not_found(dataframe):
        if checkpoint_passed(dataframe, start_date):
            return items_not_found_in_dataframe(dataframe, checkpoint)
        else:
            return True
    return not_found

CHECKERS = dict(
    a=[not_found_factory(VALUES_ANNUAL_1999), 
       # FIXME:
       #not_found_factory_conditional(VALUES_ANNUAL_2017, '2017')
       ],
    q=[not_found_factory(VALUES_QTR_1999)],
    m=[not_found_factory(VALUES_MONTHLY_1999)]
)

def omissions(dfs): 
    return [x for freq in 'aqm' 
              for not_found in CHECKERS[freq] 
              for x in not_found(dfs[freq])]


def uncovered_columns(df, cp_list: list):
    """
    Returns column names in dataframe *df*
    that are not covered by *checkpoints*.

    Args:
        df (pandas dataframe): parsing result
        checkpoints: list of dictionaries
    Returns:
        list of column names not matched by *checkpoints*
    """
    checkpoint_column_names = [key for cp in cp_list
                                   for key in cp['values'].keys()]
    diff = set(df.columns).difference(set(checkpoint_column_names)) \
                          .difference(['year', 'month', 'qtr'])
    return list(diff)                          

CHECKERS2 = dict(
    a=lambda df: uncovered_columns(df, [VALUES_ANNUAL_1999, VALUES_ANNUAL_2017]),
    q=lambda df: uncovered_columns(df, [VALUES_QTR_1999]),
    m=lambda df: uncovered_columns(df, [VALUES_MONTHLY_1999])
)

def orphans(dfs):
    return [{freq: x} for freq in 'aqm' 
                      for x in CHECKERS2[freq](dfs[freq])]
    
    
class ValidationError(ValueError):
    pass
   
            

## TODO (EP): add QTR_STR_2016
## TODO (EP): add MONTH_STR_2016
## TODO (EP): for optional checkpoints need textual description, eg. 
##            "in releases prior to 2016 INDPRO and PPI is Nan, we check it 
##             with additional values for 2016."
#OPTIONAL_CHECKPOINTS = dict(
#    a=CheckpointList(ANNUAL_STR_2016),
#    q=[],
#    m=[],
#)
#
#
#def is_found(df, d):
#    """Return true if dictionary *d* value
#       if found in dataframe *df*.
#    """
#    try:
#        return df.loc[d.date, d.name].iloc[0] == d.value
#    except KeyError:
#        return False





def validate(df, checkpoints):
    """Validate dataframe *df* with list of dictionaries
       *checkpoints*.
    """
    missed = find_missed_checkpoints(df, checkpoints)
    if missed:
        raise ValidationError(f"Required checkpoints not found in dataframe: {missed}")

    uncovered = find_uncovered_column_names(df, checkpoints)
    if uncovered:
        raise ValidationError(f"Variables not covered by checkpoints: {uncovered}")


def validate2(df, required_checkpoints, additional_checkpoints, strict=False):
    """
    Validate dataframe *df* against *required_checkpoints* and *optional_checkpoints*. 
    *strict* flag controls exception/warning handling. 

    Step 1. Are all checkpoints found in frame?

    There are required and optional (additional) checkpoints.  
    We raise ValueError if any required checkpoint is missed.
    
    Step 2. Are there any dataframe columns not covered by non-Nan checkpoints?

    Raise warning if dataframe *df* contains any variables which are not covered by
    checkpoints (either required or optional).

    Args:
        df: parsing result as pandas dataframe
        required_checkpoints(list of dictionaries): required checkpoints
        additional_checkpoints(list of dictionaries): optional checkpoints
        strict(bool): if True raise exceptions for warnings
        optional checkpoint and only shows warning otherwise

    Raises:
        Error or warning on unexpected result 
    """
    freq = required_checkpoints[0].freq
    
    def echo(msg, strict):
        if strict:
            raise ValidationError(msg)
        else:
            # print is not blocking the flow in batch process
            print(msg)

    # this is "Step 1"
    missed_required = find_missed_checkpoints(df, required_checkpoints)
    missed_optional = find_missed_checkpoints(df, additional_checkpoints)

    if missed_required:
        msg = f"Required checkpoints not found in dataframe: {missed_required}"
        echo(msg, True)
    if missed_optional:
        msg = f"Optional checkpoints not found in dataframe: {missed_optional}"
        echo(msg, strict)

    # this is "Step 2" 
    uncovered_required = find_uncovered_column_names(df, required_checkpoints)
    uncovered_optional = find_uncovered_column_names(df, additional_checkpoints)

    # ensure a variable in dataframe is covered by at least one checkpoint
    # we use `intersection` here because we need to find columns which
    # are not covered by both required AND optional checkpoints
    # if both of them miss the column, it is uncovered
    uncovered = uncovered_required.intersection(uncovered_optional)
    if uncovered:
        msg = (f'Variables in dataframe not covered by checkpoints {uncovered}'
               f' at frequency <{freq}>.')
        echo(msg, strict)


def find_missed_checkpoints(df, checkpoints):
    """
    Returns checkpoints not found in dataframe *df*.

    Args:
        df (pandas dataframe): parsing result
        checkpoints: list of dictionaries

    Returns:
        list *checkpoints* not found in dataframe *df*
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
