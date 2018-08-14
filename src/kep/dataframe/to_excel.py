"""Save xls file."""

import pandas as pd


def save_excel(filepath: str, a, q, m):
    """Save *dataframes* as .xlsx at *filepath*."""
    with pd.ExcelWriter(filepath) as writer:
        a.to_excel(writer, sheet_name='year')
        q.to_excel(writer, sheet_name='quarter')
        m.to_excel(writer, sheet_name='month')
        # TODO: add variable names
        # self.df_vars().to_excel(writer, sheet_name='variables')
    return 'Saved Excel file to {}'.format(filepath)
