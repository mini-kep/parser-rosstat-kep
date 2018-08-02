from kep.session import Session 
from locations import date_span, interim_csv, unit_mapper, parsing_instructions

from profilehooks import profile, timecall


ALL_DATES = date_span('2009-04', '2018-04')

def get_frames(s):
    dfa, dfq, dfm = s.dataframes()
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty 
    
@profile(immediate=True, entries=20, filename='runtime.txt')
#@timecall(immediate=True)
def search_all():
    s = Session(unit_mapper(), parsing_instructions())
    for year, month in ALL_DATES:
        print('Parsing', year, month)
        csv_source = interim_csv(year, month)
        s.parse(csv_source)
    
if __name__ == '__main__':     
    #s = Session(unit_mapper(), parsing_instructions())
    #for year, month in ALL_DATES:
    #    print('Parsing', year, month)
    #    csv_source = interim_csv(year, month)
    #    s.parse(csv_source)
    search_all()

# Profiling reference:
# https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code/

# Ideas:
# - why so many calls to split_to_tables? expected 108*5.
# - filter.py very time consuming, specifically is_year(), get_year()
# - 1021347 calls so 

"""
   Ordered by: cumulative time, internal time, call count
   List reduced from 228 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.136    0.136    5.950    5.950 playground.py:15(search_all)
      108    0.006    0.000    5.763    0.053 session.py:28(parse)
      108    0.754    0.007    4.736    0.044 reader.py:51(split_to_tables)
   598899    0.422    0.000    2.219    0.000 filters.py:28(clean_year)
   667889    0.271    0.000    1.867    0.000 re.py:179(search)
   599611    1.498    0.000    1.586    0.000 reader.py:26(read_csv_from_file)
   667889    1.128    0.000    1.187    0.000 re.py:286(_compile)
      324    0.001    0.000    1.021    0.003 parser.py:190(wrapper)
      324    0.002    0.000    1.012    0.003 parser.py:175(get_parsed_tables)
      324    0.000    0.000    0.722    0.002 parser.py:32(__init__)
      324    0.103    0.000    0.722    0.002 parser.py:95(parse_units)
   197340    0.462    0.000    0.512    0.000 units.py:14(extract)
   667891    0.409    0.000    0.409    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
     2160    0.003    0.000    0.276    0.000 parser.py:42(apply)
      216    0.017    0.000    0.252    0.001 parser.py:53(start_with)
    49606    0.051    0.000    0.247    0.000 reader.py:115(contains_any)
   174403    0.066    0.000    0.143    0.000 reader.py:92(headers)
   599503    0.095    0.000    0.095    0.000 filters.py:42(is_allowed)
   174403    0.078    0.000    0.078    0.000 reader.py:95(<listcomp>)
     6567    0.011    0.000    0.065    0.000 codecs.py:318(decode)
"""      