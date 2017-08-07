import pandas as pd

from kep import locate_csv
from kep import csv2frames 
from kep import DEFAULT_SPEC
from kep import CHECKPOINTS

#each month release is addressed by year and month
year, month = 2017, 5

# get csv file 'path' from 'data/interim folder'
path = locate_csv(year, month)

# parse csv file form 'path' using 'spec' inputs 
# note: df is DataHolder class
df = csv2frames(path, spec=DEFAULT_SPEC)

# control values are read
# TODO: need new validation procedure
if not df.includes(CHECKPOINTS):
    msg = df.get_error_message(CHECKPOINTS)
    raise ValueError(msg)

# pandas dataframes at different frequencies
dfa = df.annual()
dfq = df.quarterly()
dfm = df.monthly()

for _df in [dfa, dfq, dfm]:
   assert isinstance(_df, pd.DataFrame) 

# save dataframes to 'data/processed' folder
df.save(year, month)