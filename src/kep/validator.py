"""
Use hardcoded constants ANNUAL, QTR and MONTHLY to validate 
*dfa*, *dfq*, *dfm* dataframes.
"""

ANNUAL = [
   ('GDP_bln_rub', 1999, 4823.0),
   ('GDP_yoy', 1999, 106.4), 
   ('AGROPROD_yoy', 1999, 103.8),
]

QTR = [('GDP_bln_rub', 1999, {4: 1447}),
       ('CPI_rog', 1999, {1: 116.0, 2: 107.3, 3: 105.6, 4: 103.9})
       ]
          
MONTHLY = [('CPI_rog', 1999, {1: 108.4, 6: 101.9, 12: 101.3}),
           ('EXPORT_GOODS_bln_usd', 1999, {12: 9.7}),
           ('IMPORT_GOODS_bln_usd', 1999, {12: 4.0})
           ]
          
def includes_period(period_field, df, checkpoint):
    label = checkpoint[0]
    if label not in df.columns:
        return False
    year = checkpoint[1]
    flags = []
    for p in checkpoint[2].keys():
        ix = (df[period_field] == p)
        df_value = df[(df.year == year) & ix][label].iloc[0]
        flags.append(df_value == checkpoint[2][p])
    return all(flags)
   
    
class ValidatorBase:
    def __init__(self, df, checkpoints):
        self.df = df
        self.checkpoints = checkpoints

    def includes(self, checkpoint):
        return True

    def not_found(self):
        return [x[0] for x in self.checkpoints if not self.includes(x)]
        
class ValidatorAnnual(ValidatorBase):
    def includes(self, checkpoint):
        label = checkpoint[0]
        if label not in self.df.columns:
            return False            
        year = checkpoint[1]
        ix = (self.df.year == year)
        df_value = self.df[ix][label].iloc[0]
        return df_value == checkpoint[2]
 
class ValidatorQtr(ValidatorBase):           
    def includes(self, checkpoint):
        return includes_period('qtr', self.df, checkpoint)
        
class ValidatorMonthly(ValidatorBase):           
    def includes(self, checkpoint):
        return includes_period('month', self.df, checkpoint)

def not_found(dfa, dfq, dfm):
    return ValidatorAnnual(dfa, ANNUAL).not_found() + \
           ValidatorQtr(dfq, QTR).not_found() + \
           ValidatorMonthly(dfm, MONTHLY).not_found() 
    
def validate(dfs):
    nf = not_found(dfs['a'], dfs['q'], dfs['m'])
    if nf:
        raise ValueError("Not found in dataset: {}".format(nf)) 
    return True         

#if __name__ == "__main__":    
#    for a in ANNUAL:
#        assert includes_annual(dfa, a)
#    
#    for q in QTR:
#        assert includes_qtr(dfq, q)
#        
#    for m in MONTHLY:
#        assert includes_monthly(dfm, m)           