from kep.session.verifier import check
from kep.parser.row import Datapoint
import pandas as pd
                
SRC = """
any:
- INDPRO_yoy:
     - a 2015 99.2
     - a 2002 103.1
- INDPRO_rog:   
    - q 2015 3 82.8
    - q 2002 3 94.0    
- INDPRO_ytd:  
    - m 2015 1 100    
    - m 2002 1 103.7        
- PROFIT_MINING_mln_rub:
    - a 2017 2595632
    - m 2017 1 258752
    - a 1999 109148        
all: 
 - CPI_NONFOOD_rog:
    - m 1999 12 101.1
"""

DATAPOINTS = [
  # any      
  Datapoint(label='INDPRO_yoy', freq='a', year=2015, month=12, value=99.2),
  #Datapoint(label='INDPRO_yoy', freq='a', year=2002, month=12, value=103.1),
  Datapoint(label='INDPRO_rog', freq='q', year=2015, month=3, value=82.8),
  #Datapoint(label='INDPRO_rog', freq='q', year=2002, month=3, value=94.0),
  Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=1, value=100.0),
  #Datapoint(label='INDPRO_ytd', freq='m', year=2002, month=1, value=103.7),
  #Datapoint(label='PROFIT_MINING_mln_rub', freq='a', year=2017, month=12, value=2595632.0),
  Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=1, value=258752.0),
  #Datapoint(label='PROFIT_MINING_mln_rub', freq='a', year=1999, month=12, value=109148.0),
  #all
  Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=12, value=101.1)
  ]

def test_check(): 
    check(SRC, DATAPOINTS)
