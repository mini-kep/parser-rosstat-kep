from kep.session import Session 
from locations import date_span, interim_csv, unit_mapper, parsing_instructions

from profilehooks import profile, timecall
from timeit import timeit 

ALL_DATES = date_span('2009-04', '2018-04')

def get_frames(s):
    dfa, dfq, dfm = s.dataframes()
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty 
    
#@profile(immediate=True, entries=20, filename='runtime.txt')
#@timecall(immediate=True)
def search_all():
    s = Session(unit_mapper(), parsing_instructions())
    for year, month in ALL_DATES:
        print('Parsing', year, month)
        csv_source = interim_csv(year, month)
        s.parse(csv_source)
    
if __name__ == '__main__':     
    x = timeit('search_all()', 'from playground import search_all', number=1)
    

# Profiling reference:
# https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code/

"""
   Ordered by: cumulative time, internal time, call count
   List reduced from 228 to 20 due to restriction <20>

   Ordered by: cumulative time, internal time, call count
   List reduced from 230 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.129    0.129    5.784    5.784 playground.py:15(search_all)
      108    0.004    0.000    5.607    0.052 session.py:28(parse)
      108    0.656    0.006    4.473    0.041 reader.py:51(split_to_tables)
   598899    0.462    0.000    2.056    0.000 filters.py:15(clean_year)
   599611    1.532    0.000    1.621    0.000 reader.py:26(read_csv_from_file)
   598899    0.225    0.000    1.595    0.000 re.py:214(findall)
   667889    0.982    0.000    1.044    0.000 re.py:286(_compile)
      324    0.001    0.000    1.022    0.003 parser.py:190(wrapper)
      324    0.002    0.000    1.013    0.003 parser.py:175(get_parsed_tables)
      324    0.000    0.000    0.720    0.002 parser.py:32(__init__)
      324    0.099    0.000    0.720    0.002 parser.py:95(parse_units)
   197340    0.464    0.000    0.515    0.000 units.py:14(extract)
   598899    0.354    0.000    0.354    0.000 {method 'findall' of '_sre.SRE_Pattern' objects}
     2160    0.003    0.000    0.279    0.000 parser.py:42(apply)
      216    0.016    0.000    0.255    0.001 parser.py:53(start_with)
    49606    0.051    0.000    0.252    0.000 reader.py:115(contains_any)
   174403    0.063    0.000    0.145    0.000 reader.py:92(headers)
    68990    0.026    0.000    0.138    0.000 re.py:179(search)
      108    0.073    0.001    0.107    0.001 session.py:30(<listcomp>)
   599503    0.087    0.000    0.087    0.000 filters.py:30(is_allowed)
"""      