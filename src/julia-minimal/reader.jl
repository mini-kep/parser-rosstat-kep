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

# FILE STRUCTURE
# --------------
"""
Header text with some variable name strings to capture, units of measurement (names and unit have different spelling in different files)
or maybe unit of mesurement is on nect line
2017 1000 200 200 300 300
2018      175
next unit of measurement
2017 1,041  1,038 1,041 1,056 1,021
2018        1,025 
"""


# MINIMAL EXAMPLE
# ---------------

table = readdlm("tab.csv", '\t')

# get size of an array 
heads = table[1:35,1]
print(heads)

#todo: split table into slices

# first encountered line is "Объем ВВП, млрд.рублей /GDP, bln rubles"
# last encountered line is 2018
# must return numeric rows 1999-2018 from 'table'
# must return table header
start_line_contains = "Объем ВВП"
table_endswith = "2018"
#slice_data, slice_header = extract(table, start_line_contains, table_endwith)


# next:
# name_mapper is a dictionary that maps "Объем ВВП" to "GDP"
# unit_mapper is a dictionary that maps "млрд.рублей" to  "bln_rub"


# name = get_name(name_mapper, slice_header) 
# unit = get_unit(unit_mapper, slice_header)
# label is name_unit
_label = "GDP_bln_rub"

# get_datapoints(data=slice_data, row_pattern="YQQQQ", label=_label)
# sort to streams of annual, quarterly and monthly data 


# ENHANCEMENTS
# ------------
# - write test for minimal example
# - same without table_endswith - stop table before when next text is encountered
# - trailing tables like "Индекс промышленного производства" + "в % к предыдущему периоду"
# - cleaning values like "20171)"