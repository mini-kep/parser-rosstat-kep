#for speed tests
import manage
from util.dataframe import (to_dataframes, create_dataframe3, 
                            make_base_dataframe, convert_labels2)
from timeit import timeit
import pandas as pd
import csv

SRC = manage.Locations(2018, 1).interim_csv
TEST_DOC = SRC.read_text(encoding='utf-8') 
TEST_GEN1 = manage.evaluate(SRC.read_text(encoding='utf-8') , manage.UNITS, manage.YAML_DOC)
TEST_GEN2 = manage.evaluate(SRC.read_text(encoding='utf-8') , manage.UNITS, manage.YAML_DOC)

def get_generator():
    return manage.evaluate(SRC.read_text(encoding='utf-8') , manage.UNITS, manage.YAML_DOC)

def iso0():
    gen = get_generator()
    for x in gen:
        pass
        
def iso1():
    gen = get_generator()  
    values = (convert_labels2(x) for x in gen if x['freq'] == 'a' and x['value'])
    dfa = pd.DataFrame.from_records(values, 
               columns = ['value', 'freq', 'time_index', 'label'])

if __name__ == '__main__':
    n = 3
    # TODO: time to beat is benchmark time *t0*
    t0 =  1 / n * timeit('iso0()', 'from timer import iso0', number=n)
    t1 =  1 / n * timeit('iso1()', 'from timer import iso1', number=n)
    print (t0, t1)

    
#    n = 3 
#    t = 1 / n
#    exec_time1 = t * timeit('isolation1()', 'from timer import isolation1', number=n)
#    exec_time1g = t * timeit('isolation1_gen()', 'from timer import isolation1_gen', number=n)
#    #exec_time2 = t * timeit('isolation2()', 'from timer import isolation2', number=n)
#    exec_time2g = t * timeit('isolation2g()', 'from timer import isolation2g', number=n)
#    exec_time3 = t * timeit('parse(2018, 1)', 'from manage import parse', number=n)
#
#    print('Operation 1 - extracting values: {:.4f}'.format(exec_time1))
#    print('Operation 1 - extracting values (gen): {:.4f}'.format(exec_time1g))
#    #print('Operation 2 - making dataframe:  {:.4f}'.format(exec_time2))
#    print('Operation 2 - making dataframe (gen):  {:.4f}'.format(exec_time2g))
#    print('Sum of operations 1 and 2:       {:.4f}'.format(exec_time3))
#    
#    """
#    Operation 1 - extracting values: 0.0027
#    Operation 2 - making dataframe:  0.2708
#    Sum of operations 1 and 2:       1.2477
#    """
#
#    # QUESTIONS:
#    # 1. why running time for `parse(2018, 1)` is 4 times greater than sum of components
#    #    if it is correctly measured
#    # 2. how can one make parse() run faster?    
#    dfs = isolation2g()
#    manage.verify(dfs['a'], 'a')
