# -*- coding: utf-8 -*-
import pandas as pd
import io

from kep.spec import Definition, Specification
from kep.rows import to_rows
from kep.tables import get_tables 
from kep.vintage import Emitter


def csvfile_to_dataframes(csvfile, spec):
    """Extract dataframes from *csvfile* using *spec* parsing instructions. 
    
    This fucntion is also contained in vintage.py, duplicated here for 
    reference.
    
    Arg:
      csvfile (file connection or StringIO) - CSV file for parsing
      spec (spec.Specification) - pasing instructions
    """
    rows = to_rows(csvfile)
    tables = get_tables(rows, spec)    
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq="a")
    dfq = emitter.get_dataframe(freq="q")
    dfm = emitter.get_dataframe(freq="m")
    return dfa, dfq, dfm

# 1. StringIO example: *csvfile1* is parsed with *spec1* instruction 

# input data
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
dfa, dfq, dfm = csvfile_to_dataframes(csvfile1, spec1)
assert isinstance(dfa, pd.DataFrame)
assert isinstance(dfq, pd.DataFrame)
assert isinstance(dfm, pd.DataFrame) 
assert dfm.empty is True

# 2. content validation procedure
from kep.validator import Validator, serialise
check_points = [{'freq': 'a', 'label': 'GDP_bln_rub', 'period': False, 'value': 4823.0, 'year': 1999},
                {'freq': 'q', 'label': 'GDP_bln_rub', 'period': 1, 'value': 901.0, 'year': 1999},
                {'freq': 'q', 'label': 'GDP_bln_rub', 'period': 4, 'value': 2044, 'year': 2000}]
checker = Validator(dfa, dfq, dfm)
for c in check_points:
    assert checker.is_included(c) 


# 3. read by month/year
from kep.vintage import Vintage
year, month = 2017, 5
vint = Vintage(year, month)
vint.validate()
dfa2, dfq2, dfm2 = vint.dfs()
# may also save to 'data/processed' folder
# vint.save()

# TODO: parse several tables with a larger parsing definitoin (from test folder)