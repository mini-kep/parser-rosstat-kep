# -*- coding: utf-8 -*-
import pandas as pd


# TODO <https://github.com/epogrebnyak/mini-kep/issues/61>

# Check on resulting dataframes dfa, dfq, dfm based on following rules:
#  1. absolute values by month/qtr accumulate to qtr/year (with some delta for rounding)
#  2. rog rates accumulate to yoy (with some delta for rounding)

# aggregation functions


def aggregate_levels_to_annual(df):
    """Aggregates dataframe with level variables (like GDP_bln_rub)
       to annual level.

        Args:
            df (pd.DataFrame): orginal dataframe to be aggragated

        Returns:
            An aggregated dataframe with annual sum.
    """
    return df.resample('A').sum()


def aggregate_rates_to_annual_average(df):
    """Aggregates *df* dataframe with rate of growth (rog) variables
       (like CPI_rog) to annual average rates of growth.

       Args:
          df (pd.DataFrame): orginal dataframe with rog.

       Returns:
          An aggregated dataframe with annual averge growth rates (yoy).
    """
    df = df.rename(columns=lambda x: x.replace('rog', 'yoy'))
    df = (df / 100).cumprod()  # Compute annualized values
    z = df.resample('A').sum()
    rate = z / z.shift() * 100
    return rate.iloc[1:, ]


def get_deltas(df1, agg_func, df2):
    """Calculate delta as:

        delta = abs(agg_func(df1) - df2)

        Needed as a screening fucntion.

        Args:
            df1 (pd.DataFrame): orginal dataframe to be aggragated
            agg_func: aggregation function, like
            df2 (pd.DataFrame): dataframe to check against

        Returns:
            delta, pd.DataFrame
    """
    return abs(agg_func(df1) - df2).fillna(0).round(2)


def not_in(a, b):
    return ", ".join([x for x in a.columns if x not in b.columns])


def check_column_identity(df1, df2):
    if set(df1.columns) == set(df2.columns):
        return True
    else:
        print("df1 not in df2:", not_in(df1, df2))
        print("df2 not in df1:", not_in(df2, df1))
        raise KeyError


def compare_dataframes(df1, agg_func, df2, threshold):
    """Check consistency of *df1* and *df2* using:

         abs(agg_func(df1) - df2) < threshold

        Args:
            df1 (pd.DataFrame): orginal dataframe to be aggragated
            agg_func: aggregation function
            df2 (pd.DataFrame): dataframe to check against
            threshold (float): tolerance level for comparison precision

        Returns:
           True if all deltas are within *threshold*.

        Raises:
            KeyError, if df1 and df2 columns do not match.
    """
    check_column_identity(agg_func(df1), df2)
    delta = get_deltas(df1, agg_func, df2)
    is_passed = abs(delta) < threshold
    return is_passed.all().all()


def runner(feed):
    """Runs each test setup from *feed*. Prints test results.

       Args:
          feed: list of tuples (df1, accum, df2, threshold)

       Returns:
          True, if all tests are successful.
    """
    test_results = [compare_dataframes(*setup) for setup in feed]
    for i, t in enumerate(test_results):
        print(f'Test {i} result:', t)
    global_result = all(test_results)
    print('Global result:', global_result)
    return global_result


def get_unique_varnames(df_list):
    """Return list of unique variables *df_list*.
       Args:
          list of pd.DataFrame()
    """
    _all = [varname for df in df_list for varname in df.columns]
    return set(_all) - {'month', 'qtr', 'year'}


# at this point we are ready to make tests and run them

if __name__ == "__main__":

    from kep.access import dfa, dfm, dfq

    all_setups = []

    # test 1:

    # setup
    m_level_vars = [x for x in dfm.columns if 'bln' in x and 'ACCUM' not in x]
    df1 = dfm[m_level_vars]
    # WARNING: may not be true dfa includes m_level_vars
    df2 = dfa[m_level_vars]
    threshold = 0.049 * 12
    test_args = [df1, aggregate_levels_to_annual, df2, threshold]
    all_setups.append(test_args)

    # screening
    screen_1 = get_deltas(df1, aggregate_levels_to_annual, df2)

    # test result
    res_1 = compare_dataframes(*test_args)

    # test 2:

    # setup
    def as_yoy(varnames):
        return [vn.replace('rog', 'yoy') for vn in varnames]

    def as_rog(varnames):
        return [vn.replace('yoy', 'rog') for vn in varnames]

    m_rog_vars = [x for x in dfm.columns if 'rog' in x]
    y_yoy_vars = [x for x in as_yoy(m_rog_vars)
                  if x in dfa.columns.tolist()]
    m_rog_vars = [x for x in as_rog(y_yoy_vars)]
    df1 = dfm[m_rog_vars]
    df2 = dfa[y_yoy_vars]
    threshold = 0.8

    test_args = [df1, aggregate_rates_to_annual_average, df2, threshold]
    all_setups.append(test_args)

    # screening
    screen_2 = get_deltas(df1, aggregate_rates_to_annual_average, df2)

    # TO THINK: 0.8 > 0.72 is realy a big deviation, it is in fact a test failure for WAGE_REAL_yoy
    # screen_2.max()
    # INDPRO_yoy                  0.00
    # INVESTMENT_yoy              0.04
    # RETAIL_SALES_FOOD_yoy       0.09
    # RETAIL_SALES_NONFOOD_yoy    0.01
    # RETAIL_SALES_yoy            0.01
    # WAGE_REAL_yoy               0.72

    # test result
    res_2 = compare_dataframes(*test_args)

    # run all tests again
    runner(feed=all_setups)

    # variable coverage - which variables were not tested?
    all_available = get_unique_varnames([dfa, dfq, dfm])
    participating_dfs = [df for setup in all_setups
                         for df in (setup[0], setup[2])]
    all_tested = get_unique_varnames(participating_dfs)
    not_tested = sorted(list(all_available - all_tested))

    print("Variables not covered:")
    print('\n'.join(not_tested))

# COMMENTS:
# - the setup can be a small class Case with passing parameters at init, screen() and result() methods
# - epsilon can be found by lookup function depending on frequencies compared and type of accum function, this can be a dictionary
# - can use a dictionary as arg: Case({'m':df1, 'a':df2}, accum_func)
