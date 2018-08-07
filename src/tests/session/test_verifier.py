from kep.session.verifier import Verifier
import pandas as pd
                
SRC = """
CPI_NONFOOD_rog:
   all:
      - m 1999  1 106.2
      - m 1999 12 101.1
   any:
      - m 1999 12 101.1
      - m 2018  5 100.9
"""


def ts(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()

_df = pd.DataFrame({'CPI_NONFOOD_rog':
                   {ts(1999, 1): 106.2,
                    ts(1999, 2): 104.0,
                       ts(1999, 3): 103.2,
                       ts(1999, 4): 104.0,
                       ts(1999, 5): 102.7,
                       ts(1999, 6): 101.6,
                       ts(1999, 7): 101.9,
                       ts(1999, 8): 102.4,
                       ts(1999, 9): 102.7,
                       ts(1999, 10): 102.2,
                       ts(1999, 11): 101.5,
                       ts(1999, 12): 101.1,
                       ts(2018, 1): 100.3,
                       ts(2018, 2): 100.1,
                       ts(2018, 3): 100.2,
                       ts(2018, 4): 100.4,
                       ts(2018, 5): 100.9,
                       ts(2018, 6): 100.4}})

def test_verifier():
    dfa, dfq, dfm = _df, _df, _df    
    v = Verifier(SRC, dfa, dfq, dfm)
    assert v.any()        
    assert v.all()        
            
