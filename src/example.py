# -*- coding: utf-8 -*-
import pandas as pd
import io

# from runner.py
from csv2df.specification import Definition, Specification
from csv2df.reader import Reader, open_csv
from csv2df.parcer import extract_tables
from csv2df.emitter import Emitter
from csv2df.validator import Validator

#from csv2df.runner.py
def get_dataframes(csvfile, spec):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Arg:
      csvfile (file connection or StringIO) - CSV file for parsing
      spec (spec.Specification) - pasing instructions, defaults to spec.SPEC
    """
    parsed_tables = []    
    # Reader.items() yeild a tuple of csv file segment and its parsing definition
    #    csv_segment - list of reader.Row instances
    #    pdef - parsing definition is specification.Definition instance    
    for csv_segment, pdef in Reader(csvfile, spec).items():
        # construct list of Table()'s from csv_segment        
        # and identify variable names and units in each table 
        tables = extract_tables(csv_segment, pdef)
        # accumulate results
        parsed_tables.extend(tables)

    # get dataframes from parsed tables
    emitter = Emitter(parsed_tables)
    dfa = emitter.get_dataframe(freq='a')
    dfq = emitter.get_dataframe(freq='q')
    dfm = emitter.get_dataframe(freq='m')
    return dfa, dfq, dfm

    
# Example 1. StringIO *csvfile1* is parsed with *spec1* instruction 

csvfile1 = io.StringIO("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles					
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")
# input instruction
main = Definition(units={'млрд.рублей':'bln_rub'})
main.append(varname='GDP',
            text='Объем ВВП',
            required_units=['bln_rub'])
spec1 = Specification(default=main)

# parsing result
dfa, dfq, dfm = get_dataframes(csvfile1, spec1)
assert isinstance(dfa, pd.DataFrame)
assert isinstance(dfq, pd.DataFrame)
assert isinstance(dfm, pd.DataFrame) 
assert dfm.empty is True


# Example 2. Parsing result validation
check_points = [{'freq': 'a', 'label': 'GDP_bln_rub', 'period': False, 'value': 4823.0, 'year': 1999},
                {'freq': 'q', 'label': 'GDP_bln_rub', 'period': 1, 'value': 901.0, 'year': 1999},
                {'freq': 'q', 'label': 'GDP_bln_rub', 'period': 4, 'value': 2044, 'year': 2000}]
checker = Validator(dfa, dfq, dfm)
for c in check_points:
    assert checker.is_included(c) 


# Example 4 Read actual data by month and year
year, month = 2017, 5

# 4.1 Access to csv file using path helper
from csv2df.helpers import PathHelper
from csv2df.specification import SPEC
csv_path = PathHelper.locate_csv(year, month)
with open_csv(csv_path) as csvfile:
    dfa1, dfq1, dfm1 = get_dataframes(csvfile, SPEC)

# 4.2 Access to csv file using vintage class
from csv2df.runner import Vintage
vint = Vintage(year, month)
dfa2, dfq2, dfm2 = vint.dfs()

assert dfa1.equals(dfa2)
assert dfq1.equals(dfq2)
assert dfm1.equals(dfm2)

# Example 5. Validation example
vint.validate()

# LATER: parse several tables with a larger parsing definition (from test folder)