# Parse data from CSV files

# PSEUDOCODE
# ---------- 
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for reach table:
#   - get data from table based on columns format like "YQQQQMMMMMMMMMMMM"
#   - select variable label based on name and unit strings contained in table header
# 4. combine data from tables into three dataframes based on frequency
# 5. write dfa, dfq, dfm to disk 

# MINIMAL EXAMPLE
# ---------------

table = readdlm("tab.csv", '\t')
heads = table[1:35,1]
print(heads)
