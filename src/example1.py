# -*- coding: utf-8 -*-
import pandas as pd
import io

from kep.spec import Definition, Specification
from kep.rows import to_rows
from kep.tables import get_tables 
from kep.vintage import Emitter


def csvfile_to_dataframes(csvfile, spec):
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
assert isinstance(dfm, pd.DataFrame) # dfm is empty

# 2. content validation procedure
from kep.vintage import Validator
check_point1 = dict(label='GDP_bln_rub', year=1999, a=4823.0, q={1:901, 4:1447})        
assert Validator(dfa, dfq, dfm).is_included(check_point1) 


# 3. read by month/year and save to 'data/processed' folder
from kep.vintage import Vintage
year, month = 2017, 5
vint = Vintage(year, month)
vint.save()
# can also validate agint checkpoints
vint.validate()

# TODO: parse several tables with a larger parsing definitoin (from test folder)
