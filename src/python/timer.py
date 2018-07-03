# for speed tests
import manage
from util.dataframe import convert_labels2
from timeit import timeit
import pandas as pd

SRC = manage.Locations(2018, 1).interim_csv
TEST_DOC = SRC.read_text(encoding='utf-8')
TEST_GEN1 = manage.evaluate(
    SRC.read_text(
        encoding='utf-8'),
    manage.UNITS,
    manage.YAML_DOC)
TEST_GEN2 = manage.evaluate(
    SRC.read_text(
        encoding='utf-8'),
    manage.UNITS,
    manage.YAML_DOC)


def get_generator():
    return manage.evaluate(
        SRC.read_text(
            encoding='utf-8'),
        manage.UNITS,
        manage.YAML_DOC)


def iso0():
    gen = get_generator()
    for x in gen:
        pass


def iso1():
    gen = get_generator()
    values = (convert_labels2(x)
              for x in gen if x['freq'] == 'a' and x['value'])
    dfa = pd.DataFrame.from_records(
        values,
        columns=[
            'value',
            'freq',
            'time_index',
            'label'])


if __name__ == '__main__':
    n = 3
    # TODO: time to beat is benchmark time *t0*
    t0 = 1 / n * timeit('iso0()', 'from timer import iso0', number=n)
    t1 = 1 / n * timeit('iso1()', 'from timer import iso1', number=n)
    print(t0, t1)

#    # QUESTIONS:
#      1. overall target: make manage.parse() run faster
#      2. specific question: make manage.evaluate() run faster
