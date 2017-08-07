# -*- coding: utf-8 -*-
import pandas as pd
import io

from kep.spec import Definition, Specification
from kep.rows import yield_csv_rows, to_rows
from kep.tables import get_tables 
from kep.vintage import Emitter
from kep.spec import SPEC

from kep.files import locate_csv

def csvfile_to_dataframes(csvfile, spec):
    rows = to_rows(csvfile1)
    tables = get_tables(rows, spec1)    
    emitter = Emitter(tables)
    dfa = emitter.get_dataframe(freq="a")
    dfq = emitter.get_dataframe(freq="q")
    dfm = emitter.get_dataframe(freq="m")
    return dfa, dfq, dfm

# StringIO example - piece *csvfile1* is parsed with *spec1* instruction 

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


#internals
rows = to_rows(csvfile1)
tables = get_tables(rows, spec1)    
emitter = Emitter(tables)
dfa = emitter.get_dataframe(freq="a")
dfq = emitter.get_dataframe(freq="q")
dfm = emitter.get_dataframe(freq="m")


VALID_DATAPOINTS = [
    dict(label='GDP_bln_rub', year=1999, a=4823.0, q={1:901, 4:1447}),
    dict(label='GDP_bln_rub', year=1999, a=4823.0, q={1:901, 4:1447})
]
        
                        
#    {'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
#    {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999},
#    {'freq': 'a', 'label': 'EXPORT_GOODS_bln_usd', 'value': 75.6, 'year': 1999},
#    {'freq': 'q', 'label': 'IMPORT_GOODS_bln_usd',
#        'qtr': 1, 'value': 9.1, 'year': 1999},
#    {'freq': 'a', 'label': 'CPI_rog', 'value': 136.5, 'year': 1999},
#    {'freq': 'm', 'label': 'CPI_rog', 'value': 108.4, 'year': 1999, 'month': 1}
# FIXME: found only in latest, need some monthly value
#    #{'freq': 'm', 'label': 'IND_PROD_yoy', 'month': 4, 'value': 102.3, 'year': 2017}
#]



class Validator():
    
    def __init__(self, dfa, dfq, dfm):
        self.dfa = dfa
        self.dfq = dfq
        self.dfm = dfm
    
    def must_include(self, pt):        
        label=pt['label']
        year=pt['year']
        if 'a' in pt.keys():
            a = pt['a']
            assert a == self.get_value(self.dfa, label, year)
        if 'q' in pt.keys():
            for q, val in pt['q'].items(): 
               assert self.get_value(self.dfq, label, year, qtr=q) == val
        if 'm' in pt.keys():    
            for m, val in pt['m'].items():
               assert self.get_value(self.dfm, label, year, month=m) == val   
                
    @staticmethod
    def get_value(df, label, year, qtr=False, month=False):
        df = df[df['year']==year]
        if qtr:
           df = df[df['qtr'] == qtr]
        elif month:
           df = df[df['month'] == month]  
        return df[label][0]


v = Validator(dfa, dfq, dfm) 
for pt in VALID_DATAPOINTS: 
    v.must_include(pt)

    # REF: need new validation procedure
    #def validate(self, valid_datapoints=VALID_DATAPOINTS):
    #    for x in valid_datapoints:
    #        if not self.frames.includes(x):
    #            msg = "Not found in dataset: {}\nFile: {}".format(
    #                x, self.csv_path)
    #            raise ValueError(msg)
    #    print("Test values parsed OK for", self)
     
                                   
assert Validator.get_value(dfa, 'GDP_bln_rub', 1999) == 4823
assert Validator.get_value(dfq, 'GDP_bln_rub', 1999, qtr=1) == 901
                        



# TODO: need new validation procedure



## TODO 2: read by month/yeatr and save 
#
#
##each month release is addressed by year and month
#year, month = 2017, 5
## get csv file 'path' from 'data/interim folder'
#path = locate_csv(year, month)
## get datframes in wrapper
#df_holder = csv2frames(path)
## assert type
#dfa = df_holder.annual()
#dfq = df_holder.quarterly()
#dfm = df_holder.monthly()
#for _df in [dfa, dfq, dfm]:
#   assert isinstance(_df, pd.DataFrame) 
## save dataframes to 'data/processed' folder
#df_holder.save(year, month)
#
#
## TODO 3: test againt checkpoints
#
#year, month = 2017, 5
#path = locate_csv(year, month)
#df_holder = csv2frames(path)
#
#VALID_DATAPOINTS = [
#    {'freq': 'a', 'label': 'GDP_bln_rub', 'value': 4823.0, 'year': 1999},
#    {'freq': 'a', 'label': 'GDP_yoy', 'value': 106.4, 'year': 1999},
#    {'freq': 'a', 'label': 'EXPORT_GOODS_bln_usd', 'value': 75.6, 'year': 1999},
#    {'freq': 'q', 'label': 'IMPORT_GOODS_bln_usd',
#        'qtr': 1, 'value': 9.1, 'year': 1999},
#    {'freq': 'a', 'label': 'CPI_rog', 'value': 136.5, 'year': 1999},
#    {'freq': 'm', 'label': 'CPI_rog', 'value': 108.4, 'year': 1999, 'month': 1}
#    # FIXME: found only in latest, need some monthly value
#    #{'freq': 'm', 'label': 'IND_PROD_yoy', 'month': 4, 'value': 102.3, 'year': 2017}
#]
#
## control values are read
## TODO: need new validation procedure
##if not df.includes(CHECKPOINTS):
##    msg = df.get_error_message(CHECKPOINTS)
##    raise ValueError(msg)

