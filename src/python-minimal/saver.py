# TODO - UNFINISHED WORKFLOW
#  - type conversions and comment cleaning    
#  - (optional) checkpoints
#  - saving to dataframes
#  - checking dataframes


from reader import to_values
from parsing_definition import NAMERS, UNITS

values = to_values('tab.csv', UNITS, NAMERS)


messed_years = set()
messed_values = set()
for v in values:
    year = v['year']
    value = v['value'].replace(',', '.').replace('…','')
    try:
        int(year)
    except:    
        messed_years.add(year)
    try: 
        float(value) if value else 0
    except:         
        messed_values.add(value)
print(list(messed_years))
print(list(messed_values))

import re
regex = re.compile(r'\s*(\d{4})')
regex_v = re.compile(r'\W*(\d*?.?\d*?)(\d\))*\W*$')
unmessed =[int(re.search(regex, x).group(0)) for x in messed_years]
# assert are betweeen 1999 and 2018 
#unmessed_v =[for x in messed_values]
for x in messed_values:
    print(re.search(regex_v, x).group(1))


#TODO: clean 1 or 2 occurences of '\d)'
  
    
    