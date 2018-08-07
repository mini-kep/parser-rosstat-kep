import random

from locations import interim_csv, unit_mapper, parsing_instructions
from kep.session import Session 
from kep.dates import supported_dates


year, month = random.choice(supported_dates()[:-12])    

def test_randomised_import():
    s = Session(unit_mapper(), parsing_instructions())
    csv_source = interim_csv(year, month)
    s.parse(csv_source)
    dfa, dfq, dfm = s.dataframes()
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty 
