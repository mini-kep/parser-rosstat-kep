"""Save xls file."""

import pandas as pd


def save_excel(filepath, dataframes):
    """Save *dataframes* .xlsx *filepath*."""
    dfa, dfq, dfm = (dataframes[freq] for freq in 'aqm')
    with pd.ExcelWriter(filepath) as writer:
        dfa.to_excel(writer, sheet_name='year')
        dfq.to_excel(writer, sheet_name='quarter')
        dfm.to_excel(writer, sheet_name='month')
        # TODO: add variable names
        #self.df_vars().to_excel(writer, sheet_name='variables')
    print('Saved Excel file to:\n    ', filepath)
