from kep.session import Session 
from locations import date_span, interim_csv, unit_mapper, parsing_instructions
from kep.reader import get_tables

from profilehooks import profile
from profilehooks import timecall

ALL_DATES = date_span('2009-04', '2018-04')


@profile(immediate=True, entries=20)
def get_tables_all():
    for year, month in ALL_DATES:
        filepath = interim_csv(year, month)        
        get_tables(filepath)
    

def get_frames(s):
    dfa, dfq, dfm = s.dataframes()
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty 
    
@profile(immediate=True, entries=20)
#@timecall(immediate=True)
def search_all():
    s = Session(unit_mapper(), parsing_instructions())
    for year, month in ALL_DATES:
        print('Parsing', year, month)
        csv_source = interim_csv(year, month)
        s.parse(csv_source)
    return s    
    
if __name__ == '__main__':     
    s = search_all()
    
    

# Profiling reference:
# https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code/

"""
*** PROFILER RESULTS ***
search_all (C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/python-minimal/playground.py:15)
function called 1 times

         6257122 function calls (6256994 primitive calls) in 4.959 seconds

   Ordered by: cumulative time, internal time, call count
   List reduced from 228 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.128    0.128    4.959    4.959 playground.py:15(search_all)
      108    0.003    0.000    4.775    0.044 session.py:28(parse)
      108    0.620    0.006    3.531    0.033 reader.py:51(split_to_tables)
   599611    1.322    0.000    1.399    0.000 reader.py:26(read_csv_from_file)
   598899    0.185    0.000    1.368    0.000 filters.py:16(has_literals)
   667459    0.244    0.000    1.322    0.000 re.py:179(search)
      324    0.001    0.000    1.107    0.003 parser.py:190(wrapper)
      324    0.001    0.000    1.100    0.003 parser.py:175(get_parsed_tables)
   667459    0.783    0.000    0.842    0.000 re.py:286(_compile)
      324    0.000    0.000    0.814    0.003 parser.py:32(__init__)
      324    0.105    0.000    0.814    0.003 parser.py:95(parse_units)
   196572    0.572    0.000    0.622    0.000 units.py:14(extract)
     2160    0.002    0.000    0.271    0.000 parser.py:42(apply)
      216    0.015    0.000    0.248    0.001 parser.py:53(start_with)
    50529    0.052    0.000    0.245    0.000 reader.py:114(contains_any)
   667461    0.236    0.000    0.236    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
      108    0.033    0.000    0.133    0.001 session.py:30(<listcomp>)
   182076    0.063    0.000    0.119    0.000 reader.py:91(headers)
    43849    0.100    0.000    0.100    0.000 reader.py:80(__init__)
   599503    0.093    0.000    0.093    0.000 filters.py:35(is_allowed)
"""      