from kep import get_csv
from kep import csv2df 
from kep import DEFAULT_SPEC
from kep import CHECKPOINTS

#each month release is addressed by 
date = dict(year=2017, month=5)

# get csv file for 'data/interim folder'
fp = get_csv(date)

# parse csv file using 'spec' imputs 
dfs = csv2df(fp, spec=DEFAULT_SPEC)

# control values are read
assert dfs.includes(CHECKPOINTS)

# dataframes at different frequencies
dfa = dfs.annual()
dfq = dfs.quarterly()
dfm = dfs.monthly()

# save dataframes to 'data/processed' folder
dfs.save(date)