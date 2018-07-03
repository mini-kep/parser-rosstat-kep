# Parse data from CSV files

# This example is work in progress to create minimal example
# Full code code is at src/python/manage.py 
# Point of entry of parsing algorithm:  src.python.dispatch.evaluate() 

# PSEUDOCODE
# ---------- 
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for reach table:
#   3.1. select variable label based on name and unit strings contained in table header
#   3.2. get data from table based on columns format like "YQQQQMMMMMMMMMMMM"
# 4. combine data from tables into three dataframes based on frequency (dfa, dfq, dfm)
# 5. write dfa, dfq, dfm as csv files to disk 

# READ CSV AND SPLIT INTO TABLES (steps 1 and 2 of pseudocode)
# ------------------------------------------------------------

import csv
import re
from enum import Enum, unique

def read_csv(file): 
    """Read csv file as list of lists / matrix"""
    fmt=dict(delimiter='\t', lineterminator='\n')
    table = []
    with open(file, 'r', encoding='utf-8') as f:
        for row in csv.reader(f, **fmt):
            table.append(row)
    return table


@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2

YEAR_CATCHER = re.compile("\D*(\d{4}).*")


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from *string* using *rx* regex.

       Returns:
           Year as integer
           False if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991 and year <= 2050:
            return year
    return False

def is_year(string: str) -> bool:
    return get_year(string) is not False


def split_to_tables(rows):
    """Yield Tab() instances from *rows* list of lists."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        # is data row?
        if is_year(row[0]):
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:
                # table ended, emit it
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.HEADERS
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)

  
class Table:
    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows

    
if __name__ == "__main__":
    # read csv    
    csv_rows = read_csv("tab.csv")
    # split csv rows to tables
    # NOTES: 
    #   - split_to_tables() is a state machine to traverse through csv file 
    #   - in julia the data structure for Table class is likely to be different     
    tables = split_to_tables(csv_rows)
