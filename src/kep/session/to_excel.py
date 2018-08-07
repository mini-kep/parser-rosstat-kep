"""Save xls file."""

import pandas as pd


def save_excel(filepath, dfa, dfq, dfm):
    """Save *dataframes* as .xlsx at *filepath*."""
    with pd.ExcelWriter(filepath) as writer:
        dfa.to_excel(writer, sheet_name='year')
        dfq.to_excel(writer, sheet_name='quarter')
        dfm.to_excel(writer, sheet_name='month')
        # TODO: add variable names
        #self.df_vars().to_excel(writer, sheet_name='variables')
    return 'Saved Excel file to {}'.format(filepath)
