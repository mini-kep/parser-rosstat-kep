"""Save xls file."""

from pathlib import Path
import pandas as pd

from access import get_dataframe

XL_PATH = str(Path(__file__).with_name('kep.xlsx'))

def to_xls(filepath, dfa, dfq, dfm):
    """Save dataframes *dfa, dfq, dfm* in .xlsx *filepath*."""
    with pd.ExcelWriter(filepath) as writer:
        dfa.to_excel(writer, sheet_name='year')
        dfq.to_excel(writer, sheet_name='quarter')
        dfm.to_excel(writer, sheet_name='month')
        # TODO: add variable names
        #self.df_vars().to_excel(writer, sheet_name='variables')

# ERROR: the excel file treats decimal separators badly

# TODO: pretty formatting of Excel file 

def save_xls(): # pragma: no cover
    dfa, dfq, dfm = (get_dataframe(freq) for freq in 'aqm')
    to_xls(XL_PATH, dfa, dfq, dfm)
    print('Saved', XL_PATH)


if '__main__' == __name__:  # pragma: no cover
   save_xls()  
