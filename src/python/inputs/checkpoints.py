"""Validate parsing result using checkpoints."""

from collections import namedtuple
import pandas as pd

var_str = 'date label value'
Annual, Qtr, Month = (namedtuple(name, 'date label value')
                      for name in 'Annual Quarter Month'.split(' '))


def make_list(cls, date, values):
    return [cls(date, k, v) for k, v in values.items()]


VALUES_ANNUAL_1999 = make_list(
    Annual,
    date='1999',
    values={
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
    })


VALUES_ANNUAL_2017 = make_list(Annual,
                               date='1999',
                               values={'INDPRO_yoy': 101.0,
                                       'PPI_rog': 108.4,
                                       'AGROPROD_yoy': 103.8}
                               )

VALUES_QTR_1999 = make_list(Qtr,
                            date='1999-03',
                            values={  # 'AGROPROD_yoy': 97.2,
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


VALUES_MONTHLY_1999 = make_list(Month,
                                date='1999-01',
                                values={  # 'AGROPROD_yoy': 96.5,
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


def contains(df: pd.DataFrame, checkpoint):
    try:
        subset = df[checkpoint.label]
    except KeyError:
        return False
    return checkpoint.value == subset.loc[checkpoint.date].iloc[0]


def missed(df: pd.DataFrame, checkpoints: list):
    return [c for c in checkpoints if not contains(df, c)]


def uncovered(df: pd.DataFrame, checkpoints: list):
    """Returns column names that are not covered by *checkpoints*."""
    checkpoint_column_names = {c.label for c in checkpoints}
    diff = set(df.columns) \
        .difference(checkpoint_column_names) \
        .difference(['year', 'month', 'qtr'])
    return list(diff)


class ValidationError(ValueError):
    pass


def raise_validation_error(message: str):
    raise ValidationError(message)


def fmt(_list):
    prefix = '\n' + ' ' * 4
    return prefix + prefix.join(map(str, _list))


def _check(df, checkpoints, examiner, exc_handler, exc_message: str):
    _missed = examiner(df, checkpoints)
    if _missed:
        exc_handler(exc_message + fmt(_missed))


def require(df, checkpoints):
    return _check(df, checkpoints,
                  examiner=missed,
                  exc_handler=raise_validation_error,
                  exc_message='Dataframe must contain:')


def expect(df, checkpoints):
    return _check(df, checkpoints,
                  examiner=missed,
                  exc_handler=print,
                  exc_message='Optional checkpoints not found in dataframe:')


def cover(df, checkpoints):
    return _check(
        df,
        checkpoints,
        examiner=uncovered,
        exc_handler=print,
        exc_message='Variables in dataframe not covered by checkpoints:')


def verify(df, freq):
    print(f'Analysing frequency <{freq}>...')
    if freq == 'a':
        require(df, VALUES_ANNUAL_1999)
        expect(df, VALUES_ANNUAL_2017)
        cover(df, VALUES_ANNUAL_1999 + VALUES_ANNUAL_2017)
    elif freq == 'q':
        require(df, VALUES_QTR_1999)
        cover(df, VALUES_QTR_1999)
    elif freq == 'm':
        require(df, VALUES_MONTHLY_1999)
        cover(df, VALUES_MONTHLY_1999)
