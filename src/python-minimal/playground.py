from kep.session import Session 
from locations import date_span, interim_csv, unit_mapper, parsing_instructions
from timeit import timeit


ALL_DATES = date_span('2009-04', '2018-04')

def get_frames(s):
    dfa, dfq, dfm = s.dataframes()
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty 
    

def search_all():
    s = Session(unit_mapper(), parsing_instructions())
    for year, month in ALL_DATES:
        print('Parsing', year, month)
        csv_source = interim_csv(year, month)
        s.parse(csv_source)


if __name__ == '__main__':           
    # TODO: suggest optimisations and speedups
    n = 1
    elapsed = timeit('search_all()', 'from playground import search_all', number=n)
    t = 1 / n * elapsed
    print(t)
    