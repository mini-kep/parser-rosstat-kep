# -*- coding: utf-8 -*-
"""Use hardcoded constants for year 1999 to validate dfa, dfq, dfm dataframes.
   These dataframes are the result of parsign procedure.

   Hardcoded constants are recorded in ANNUAL, QTR and MONTHLY variables,
   converted to dictionaries using *serialise()*. CHECKPOINTS holds all
   sample datapoints as dictionaries.

   Validator(dfa, dfq, dfm).run() tests dataframes against CHECKPOINTS.
"""



ANNUAL = [('GDP_bln_rub', 1999, 4823.0),
          ('GDP_yoy', 1999, 106.4)
          ]

QTR = [('GDP_bln_rub', 1999, {4: 1447}),
       ('CPI_rog', 1999, {1: 116.0, 2: 107.3, 3: 105.6, 4: 103.9})
       ]

MONTHLY = [('CPI_rog', 1999, {1: 108.4, 6: 101.9, 12: 101.3}),
           ('EXPORT_GOODS_bln_usd', 1999, {12: 9.7}),
           ('IMPORT_GOODS_bln_usd', 1999, {12: 4.0})
           ]

def includes_annual(dfa, checkpoint):
    label = checkpoint[0]
    year = checkpoint[1]
    df_value = dfa[dfa.year == year][label].iloc[0]
    return df_value == checkpoint[2]


def includes_period(period_field, df, checkpoint):
    label = checkpoint[0]
    year = checkpoint[1]
    flags = []
    for p in checkpoint[2].keys():
        ix = (df[period_field] == p)
        df_value = df[(df.year == year) & ix][label].iloc[0]
        flags.append(df_value == checkpoint[2][p])
    return all(flags)


def includes_qtr(df, checkpoint):
    return includes_period('qtr', df, checkpoint)

def includes_monthly(df, checkpoint):
    return includes_period('month', df, checkpoint)

def not_found(dfa, dfq, dfm):
    return [a for a in ANNUAL if not includes_annual(dfa, a)] + \
           [q for q in QTR if not includes_qtr(dfq, q)] + \
           [m for m in MONTHLY if not includes_monthly(dfm, m)] 
    

def validate(dfs):
    nf = not_found(dfs['a'], dfs['q'], dfs['m'])
    if nf:
        raise ValueError("Not found in dataset: {}".format(nf)) 
    return True         

if __name__ == "__main__":    
    for a in ANNUAL:
        assert includes_annual(dfa, a)
    
    for q in QTR:
        assert includes_qtr(dfq, q)
        
    for m in MONTHLY:
        assert includes_monthly(dfm, m)           