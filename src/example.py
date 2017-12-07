"""Key examples to csv2df parser.

Workflow as follows (doc/pseudo.rst)

+----------------------------------------------+--------------------------+
| Step                                         | Call                     |
+==============================================+==========================+
| 1. Open csv file as connection               | reader.open_csv()        |
+----------------------------------------------+--------------------------+
| 2. Convert file to list of Rows instances    |                          |
+----------------------------------------------+                          |
| 3. Split list to segments and                |                          |
|    get parsing definition for each segment   | reader.Reader().items()  |
+----------------------------------------------+                          |
| 4. Supply segment and a parsing definition   |                          |
|    for further processing                    |                          |
+----------------------------------------------+--------------------------+
| 5. Create Table instances from rows          |                          |
|                                              | parser.extract_tables()  |
+----------------------------------------------+                          |
| 6. Extract variable name and unit of         |                          |
|    measurement from each table               |                          |
+----------------------------------------------+                          |
| 7. Filter defined tables and check all       |                          |
|    required variables were read              |                          |
+----------------------------------------------+--------------------------+
| 8. Submit tables to Emitter instance         |                          |
+----------------------------------------------+                          |
| 9. Import datapoints from table datarows     | emitter.Emitter()        |
|    by frequency                              |                          |
+----------------------------------------------+                          |
| 10. Create dataframes from datapoints        |                          |
|     by frequency                             |                          |
+----------------------------------------------+--------------------------+
| 11. Validate data in dataframes              | validator.Validator()    |
+----------------------------------------------+--------------------------+
| 12. Save dataframes as csv files             | Vintage().save()         |
+----------------------------------------------+--------------------------+
"""

import pandas as pd
import io

from config import InterimCSV
from csv2df.specification import Definition, Specification, SPEC
from csv2df.reader import Reader, open_csv
from csv2df.parser import extract_tables
from csv2df.emitter import Emitter
from csv2df.runner import Vintage
from csv2df.validator import Validator



# copied from csv2df.runner.py

def get_dataframes(csvfile, spec):
    """Extract dataframes from *csvfile* using *spec* parsing instructions.

    Arg:
       csvfile (file connection or StringIO) - CSV file for parsing
       spec (spec.Specification) - pasing instructions, defaults to spec.SPEC
    Returns:
       a tuple of dataframes       
    """

    # Reader.items() yeild a tuple of csv file segment and its parsing definition
    #    csv_segment - list of reader.Row instances
    #    pdef - parsing definition is specification.Definition instance
    # We construct list of Table()'s from csv_segment and identify
    # variable names and units in each table
    parsed_tables = []
    for csv_segment, pdef in Reader(csvfile, spec).items():
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

# data
csvfile1 = io.StringIO("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")

# parsing instruction
main = Definition(units={'млрд.рублей': 'bln_rub'})
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
check_points = [{'freq': 'a',
                 'label': 'GDP_bln_rub',
                 'period': False,
                 'value': 4823.0,
                 'year': 1999},
                {'freq': 'q',
                 'label': 'GDP_bln_rub',
                 'period': 1,
                 'value': 901.0,
                 'year': 1999},
                {'freq': 'q',
                 'label': 'GDP_bln_rub',
                 'period': 4,
                 'value': 2044,
                 'year': 2000}]
checker = Validator(dfa, dfq, dfm)
for c in check_points:
    assert checker.is_included(c)

# Example 3 Read actual data by month and year
year, month = 2017, 5

# 3.1 Access to csv file using config.InterimCSV
csv_path = InterimCSV(year, month).path
with open_csv(csv_path) as csvfile:
    dfa1, dfq1, dfm1 = get_dataframes(csvfile, SPEC)

# 3.2 Access to csv file using Vintage class (identical to 3.1)
vint = Vintage(year, month)
dfs_dict = vint.dfs
dfa2, dfq2, dfm2 = [dfs_dict[freq] for freq in 'aqm']
assert dfa1.equals(dfa2)
assert dfq1.equals(dfq2)
assert dfm1.equals(dfm2)

# Example 4. validation
assert vint.validate()

def show_dicts(df=dfq):
    """Demo for serialising a DataFrame"""
    types = ['dict', 'list', 'series', 'split', 'records', 'index']
    for t in types:
        print()
        print('Serialising example', t)
        print(df.to_dict(t))
show_dicts()
