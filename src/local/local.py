# -*- coding: utf-8 -*-
"""
Created on Thu May 18 18:24:52 2017

@author: PogrebnyakEV
"""
import shutil
import re
from pathlib import Path 
src_folder = Path("T:/DMPKA_Macro/Library/gks/СЭП/краткосрочные")
destination_folder = Path("D:/digital/kep_data")

def split_base(basename):
    if basename.startswith("20"):
        # "2016_03"
        year, month = re.findall("20(\d\d)_(\d\d)", basename)[0]        
    else:
        # (ind)0117.[zip|rar]
        month, year = re.findall("\s*(\d\d)(\d\d)", basename)[0] 
    return "20"+year, month

def get_year_month_ext(filename):
    base = filename.split(".")[0]
    ext = filename.split(".")[1]    
    year, month = split_base(base)
    return month, year, ext 

for fn in destination_folder.iterdir():
    if fn.name.endswith("zip") or fn.name.endswith("rar"):
       month, year, ext = get_year_month_ext(fn.name)
       new_fn = year + "_" + month + "." + ext  
       #print (fn.name, new_fn)
       #fn.rename(fn.with_name(new_fn))
       #dst = destination_folder / fn.name
       #shutil.copyfile(fn, dst)

assert get_year_month_ext("2016_12.rar") == ('12', '2016', 'rar')
assert get_year_month_ext("ind1216.rar") == ('12', '2016', 'rar')

def get_csv_filename(year, month):
    return "tab_{}_{}.csv".format(year, month)  

def get_csv_path(year, month):
    return destination_folder / "csv" / get_csv_filename(year, month)

def all_dates():
    for y in range(2009, 2017+1):
        for m in range (1, 12+1):
            yield (str(y), str(m).zfill(2))
            
ad = list(all_dates())

for d in destination_folder.iterdir():
    if d.is_dir() and d.name != "csv":
        new_csv = d / "tab.csv"        
        year, month = split_base(d.name)
        ad.remove((year, month))
        dst = get_csv_path(year, month)
        #shutil.copy(new_csv, dst)
        #print(new_csv, "copied to", dst)

print (ad)
# Missing ('2013', '11'), but not critical - ask SA
