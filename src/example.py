# -*- coding: utf-8 -*-
import pandas as pd
import io

# from runner.py
from csv2df.specification import Definition, Specification
from csv2df.reader import Reader, open_csv
from csv2df.parcer import get_tables
from csv2df.emitter import Emitter
from csv2df.validator import Validator

def get_dataframes(csvfile, spec):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Arg:
      csvfile (file connection or StringIO) - CSV file for parsing
      spec (spec.Specification) - pasing instructions, defaults to spec.SPEC
    """

    # reader will create parsing jobs, each job is a tuple of csv file segment and its parsing definition
    #  - csv file segment is a list of reader.Row instances
    #  - parsing definition is specification.Definition instance
    parse_jobs = Reader(csvfile, spec).items()

    # construct Table class instances and identify variable names and units in each table
    tables = get_tables(parse_jobs)

    # get data from tables
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq='a')
    dfq = emitter.get_dataframe(freq='q')
    dfm = emitter.get_dataframe(freq='m')
    return dfa, dfq, dfm
    
    
# Example 1. StringIO *csvfile1* is parsed with *spec1* instruction 

csvfile1 = io.StringIO("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles					
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")
# input instruction
main = Definition(units={"млрд.рублей":"bln_rub"})
main.append(varname="GDP",
            text="Объем ВВП",
            required_units=["bln_rub"])
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
#vint.validate()

# LATER: parse several tables with a larger parsing definitoin (from test folder)
# LATER: use this example in testing +  bring good examples from testing to here 
# FIXME: test code for pandas dataframe
#from io import StringIO
#_source = StringIO("""time_index,EXPORT_GOODS_TOTAL_bln_usd,GDP_bln_rub\n1999-12-31,75.6,4823.0""")
#df = read_csv(source=_source)
#assert df.EXPORT_GOODS_TOTAL_bln_usd['1999-12-31'] == 75.6
#assert df.GDP_bln_rub['1999-12-31'] == 4823.0