#for speed tests
import manage
from timeit import timeit


SRC = manage.Locations(2018, 1).interim_csv
TEST_DOC = SRC.read_text(encoding='utf-8') 
TEST_VALUES = list(manage.evaluate(TEST_DOC, manage.UNITS, manage.YAML_DOC))

def isolation1(): 
    doc = SRC.read_text(encoding='utf-8') 
    return list(manage.evaluate(doc, manage.UNITS, manage.YAML_DOC))

def isolation2():
    dfs = {}
    for freq in 'aqm':
        df = manage.create_dataframe(TEST_VALUES, freq)
        dfs[freq] = df
        manage.verify(df, freq)        
        df.to_csv('temp.txt')
    return dfs    

if __name__ == '__main__':
    n = 10
    exec_time1 = 1/n*timeit('isolation1()', 'from timer import isolation1', number=n)
    exec_time2 = 1/n*timeit('isolation2()', 'from timer import isolation2', number=n)
    exec_time3 = 1/n*timeit('parse(2018, 1)', 'from manage import parse', number=n)

    print('Operation 1 - extracting values: {:.4f}'.format(exec_time1))
    print('Operation 2 - making dataframe:  {:.4f}'.format(exec_time2))
    print('Sum of operations 1 and 2:       {:.4f}'.format(exec_time3))
    
    """
    Operation 1 - extracting values: 0.0027
    Operation 2 - making dataframe:  0.2708
    Sum of operations 1 and 2:       1.2477
    """

    # QUESTIONS:
    # 1. why running time for `parse(2018, 1)` is 4 times greater than sum of components
    #    if it is correctly measured
    # 2. how can one make parse() run faster?     
    
