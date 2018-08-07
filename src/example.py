from kep.session import Session, Verifier
from kep.dates import date_span
from locations import interim_csv, unit_mapper, parsing_instructions, checkpoints

from profilehooks import profile

ALL_DATES = date_span('2009-04', '2018-06')


@profile(immediate=True, entries=20)
def search_all():
    s = Session(unit_mapper(), parsing_instructions())
    for year, month in ALL_DATES:
        print('Parsing', year, month)
        csv_source = interim_csv(year, month)
        s.parse(csv_source)
        dfa, dfq, dfm = s.dataframes()
        v = Verifier(checkpoints(), dfa, dfq, dfm)
        v.any()
        v.all()
    return s


if __name__ == '__main__':
    s = search_all()


# Profiling reference:
# https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code

# Packaging reference:
# http://python-packaging.readthedocs.io/en/latest/testing.html

"""
*** PROFILER RESULTS ***
search_all (C:/Users/PogrebnyakEV/Desktop/mini-kep/kep/src/example.py:10)
function called 1 times

         6454085 function calls (6453987 primitive calls) in 3.758 seconds

   Ordered by: cumulative time, internal time, call count
   List reduced from 243 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.020    0.020    3.758    3.758 example.py:10(search_all)
      110    0.004    0.000    3.644    0.033 session.py:19(parse)
      110    0.000    0.000    2.906    0.026 reader.py:27(get_tables)
      110    0.524    0.005    2.864    0.026 reader.py:50(split_csv)
   606762    0.165    0.000    1.618    0.000 reader.py:19(is_data_row)
   712245    0.251    0.000    1.535    0.000 re.py:179(search)
   606762    0.173    0.000    1.453    0.000 reader.py:16(has_literals)
   712245    0.675    0.000    0.733    0.000 re.py:286(_compile)
   609513    0.122    0.000    0.554    0.000 reader.py:32(read_csv)
   712247    0.551    0.000    0.551    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
      330    0.001    0.000    0.373    0.001 worker.py:79(apply_all)
     1650    0.001    0.000    0.372    0.000 worker.py:71(apply)
    50255    0.061    0.000    0.350    0.000 reader.py:114(contains_any)
      220    0.016    0.000    0.346    0.002 worker.py:97(start_with)
      110    0.000    0.000    0.327    0.003 worker.py:61(__init__)
      110    0.036    0.000    0.326    0.003 worker.py:139(parse_units)
    94318    0.272    0.000    0.291    0.000 units.py:17(extract)
      112    0.229    0.002    0.289    0.003 {method 'read' of '_io.TextIOWrapper' objects}
      110    0.133    0.001    0.133    0.001 {method 'splitlines' of 'str' objects}
   609403    0.097    0.000    0.097    0.000 reader.py:24(is_allowed)
"""
