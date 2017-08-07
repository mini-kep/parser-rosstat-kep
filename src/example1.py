# -*- coding: utf-8 -*-
import io

from kep.spec import Definition, Specification
from kep.rows import to_rows
from kep.tables import get_tables 
from kep.vintage import Emitter, Validator


def csvfile_to_dataframes(csvfile, spec):
    rows = to_rows(csvfile)
    tables = get_tables(rows, spec)    
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq="a")
    dfq = emitter.get_dataframe(freq="q")
    dfm = emitter.get_dataframe(freq="m")
    return dfa, dfq, dfm

# 1. StringIO example - piece *csvfile1* is parsed with *spec1* instruction 

# data
csvfile1 = io.StringIO("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles					
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")
# instruction
main = Definition(units={"млрд.рублей":"bln_rub"})
main.append(varname="GDP",
            text="Объем ВВП",
            required_units=["bln_rub"])
spec1 = Specification(default=main)
#result
dfa, dfq, dfm = csvfile_to_dataframes(csvfile1, spec1)


# 2. content validation procedure
check_point = dict(label='GDP_bln_rub', year=1999, a=4823.0, q={1:901, 4:1447})        
Validator(dfa, dfq, dfm).must_include(check_point) 


# 3/ read by month/yeatr and save 
from kep.vintage import Vintage
year, month = 2017, 5
vint = Vintage(year, month)
vint.save()      