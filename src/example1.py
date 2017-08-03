import pandas as pd

from kep import locate_csv
from kep import csv2frames 
from kep import DEFAULT_SPEC, UNITS
from kep import CHECKPOINTS

#each month release is addressed by year and month
year, month = 2017, 5

# get csv file 'path' from 'data/interim folder'
path = locate_csv(year, month)

# parse csv file form 'path' using 'spec' inputs 
dfs = csv2frames(path, spec=DEFAULT_SPEC, units=UNITS)

# control values are read
if not dfs.includes(CHECKPOINTS):
    msg = dfs.get_error_message(CHECKPOINTS)
    raise ValueError(msg)

# pandas dataframes at different frequencies
dfa = dfs.annual()
dfq = dfs.quarterly()
dfm = dfs.monthly()

for _df in [dfa, dfq, dfm]:
   assert isinstance(_df, pd.DataFrame) 

# save dataframes to 'data/processed' folder
dfs.save(year, month)