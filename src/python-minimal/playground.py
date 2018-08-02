from kep.session import Session 
from locations import date_span, interim_csv, unit_mapper, parsing_instructions

from profilehooks import profile


ALL_DATES = date_span('2009-04', '2018-04')

def get_frames(s):
    dfa, dfq, dfm = s.dataframes()
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty 
    
@profile(immediate=True, entries=40, filename='runtime.txt')
#@timecall(immediate=True)
def search_all():
    s = Session(unit_mapper(), parsing_instructions())
    for year, month in ALL_DATES:
        print('Parsing', year, month)
        csv_source = interim_csv(year, month)
        s.parse(csv_source)
        
search_all()

# Ideas:
# - why so many calls to split_to_tables? expected 108*5.
# - filter.py very time consuming, specifically is_year(), get_year()
# - 1021347 calls so 

"""
*** PROFILER RESULTS ***
search_all (C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/python-minimal/playground.py:17)
function called 1 times

         11238969 function calls (11238841 primitive calls) in 8.426 seconds

   Ordered by: cumulative time, internal time, call count
   List reduced from 254 to 40 due to restriction <40>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.129    0.129    8.426    8.426 playground.py:17(search_all)   
      108    0.006    0.000    8.250    0.076 session.py:28(parse)
      108    0.009    0.000    4.741    0.044 reader.py:19(import_tables)
    41563    0.657    0.000    4.242    0.000 reader.py:50(split_to_tables)    # why 41563 calls? 540 expected
      324    0.001    0.000    3.503    0.011 parser.py:188(wrapper)
      324    0.002    0.000    3.492    0.011 parser.py:173(get_parsed_tables)
     2160    0.002    0.000    2.647    0.001 parser.py:42(apply)
   598899    0.192    0.000    2.369    0.000 filters.py:26(is_year)           # very slow
      540    0.001    0.000    2.347    0.004 parser.py:161(datapoints)        # maybe emit nothing until dataframe creation?
      540    0.030    0.000    2.310    0.004 parser.py:166(<listcomp>)        # maybe emit nothing until dataframe creation?
   177745    0.052    0.000    2.279    0.000 reader.py:116(emit_datapoints)   # maybe emit nothing until dataframe creation?
   189669    0.454    0.000    2.223    0.000 row.py:46(emit_datapoints)       # maybe emit nothing until dataframe creation?
   598899    0.427    0.000    2.178    0.000 filters.py:12(get_year)          # very slow
      432    0.008    0.000    2.007    0.005 parser.py:157(any)
   598899    0.222    0.000    1.689    0.000 re.py:169(match)
  1021347    1.573    0.000    1.666    0.000 re.py:286(_compile)              # why calls to re._complie?
   422448    0.167    0.000    1.255    0.000 re.py:179(search)
   599611    1.057    0.000    1.058    0.000 reader.py:32(read_bytes_as_csv)  # why 599611 calls? read directly from file if it is a file.
   176557    0.199    0.000    1.019    0.000 filters.py:37(clean_value)
      324    0.001    0.000    0.831    0.003 parser.py:32(__init__)
      324    0.106    0.000    0.830    0.003 parser.py:93(parse_units)
   201633    0.576    0.000    0.626    0.000 units.py:14(extract)
   422450    0.571    0.000    0.571    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
   176557    0.147    0.000    0.529    0.000 filters.py:30(clean_year)
      110    0.009    0.000    0.508    0.005 util.py:66(wrapper)
      110    0.002    0.000    0.408    0.004 util.py:51(_read_source)
      108    0.002    0.000    0.364    0.003 parser.py:153(all)
      110    0.047    0.000    0.351    0.003 pathlib.py:1171(read_text)
   598907    0.317    0.000    0.317    0.000 {method 'match' of '_sre.SRE_Pattern' objects}
      110    0.234    0.002    0.293    0.003 {method 'read' of '_io.TextIOWrapper' objects}
      216    0.016    0.000    0.253    0.001 parser.py:51(start_with)
    49608    0.052    0.000    0.250    0.000 reader.py:108(contains_any)
   173973    0.064    0.000    0.133    0.000 reader.py:85(headers)
   857055    0.107    0.000    0.107    0.000 {method 'group' of '_sre.SRE_Match' objects}
   177637    0.058    0.000    0.102    0.000 <string>:12(__new__)
   966101    0.096    0.000    0.096    0.000 {built-in method builtins.isinstance}
   599503    0.087    0.000    0.087    0.000 filters.py:44(is_allowed)
      108    0.073    0.001    0.073    0.001 reader.py:37(read_csv)
   173973    0.069    0.000    0.069    0.000 reader.py:88(<listcomp>)
      110    0.000    0.000    0.059    0.001 codecs.py:318(decode)
"""      