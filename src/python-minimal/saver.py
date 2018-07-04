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
    value = v['value'].replace(',', '.')
    try:
        int(year)
    except:    
        messed_years.add(year)
    try: 
        float(value)
    except:         
        messed_values.add(value)
print(list(messed_years))
print(list(messed_values))

#TODO: clean 1 or 2 occurences of '\d)'
  
    
    