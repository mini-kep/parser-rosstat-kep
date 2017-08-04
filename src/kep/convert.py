# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 01:25:34 2017

@author: Евгений
"""
from kep.rows import read_csv
from kep.vintage import Frames 
from kep.tables import get_tables



            
if __name__ == "__main__":
    from kep import files
    from kep import rows
    from spec import SPEC
    csv_path = files.locate_csv()
    _rows = rows.read_csv(csv_path)
    tables = get_tables(_rows, spec=SPEC)
    for t in tables:
        print()
        print(t)            


