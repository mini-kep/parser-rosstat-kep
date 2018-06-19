"""Save xls file."""

import pandas as pd

#from kep.access import get_dataframe
#from kep.helper.path import XL_PATH


def to_xls(filepath, dfa, dfq, dfm):
    """Save dataframes *dfa, dfq, dfm* in .xlsx *filepath*."""
    with pd.ExcelWriter(filepath) as writer:
        dfa.to_excel(writer, sheet_name='year')
        dfq.to_excel(writer, sheet_name='quarter')
        dfm.to_excel(writer, sheet_name='month')
        # TODO: add variable names
        #self.df_vars().to_excel(writer, sheet_name='variables')

# ERROR: the excel file treats decimal separators badly


def save_xls(): # pragma: no cover
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    to_xls(XL_PATH, dfa, dfq, dfm)
    print('Saved', XL_PATH)


if '__main__' == __name__:  # pragma: no cover
    dfa = get_dataframe('a')
    dfq = get_dataframe('q')
    dfm = get_dataframe('m')
    save_xls()
