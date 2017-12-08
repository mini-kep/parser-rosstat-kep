import pytest

import io

from csv2df.specification import Definition, Specification
from csv2df.reader import Reader
from csv2df.parser import extract_tables
from csv2df.emitter import Emitter
from vintage import get_dataframes, Vintage, Collection
from csv2df.validator import Validator

# input data
csvfile1 = io.StringIO("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")
# input instruction
main = Definition(units={"млрд.рублей": "bln_rub"})
main.append(varname="GDP",
            text="Объем ВВП",
            required_units=["bln_rub"])
spec1 = Specification(default=main)


# parsing result
parsed_tables = []
for csv_segment, pdef in Reader(csvfile1, spec1).items():
    tables = extract_tables(csv_segment, pdef)
    parsed_tables.extend(tables)
emitter = Emitter(parsed_tables)
dfa = emitter.get_dataframe(freq='a')
dfq = emitter.get_dataframe(freq='q')
dfm = emitter.get_dataframe(freq='m')


def test_get_dataframes():
    # csvfile1 was consumed once, buffer position if not at zero
    if csvfile1.tell() != 0:
        csvfile1.seek(0)
    # Hayk: get_dataframes return a dictionary of dataframes
    #dfa_, dfq_, dfm_ = get_dataframes(csvfile1, spec1)
    dict_dfs = get_dataframes(csvfile1, spec1)
    dfa_ = dict_dfs['a']
    dfq_ = dict_dfs['q']
    dfm_ = dict_dfs['m']
    assert dfa_.equals(dfa)
    assert dfq_.equals(dfq)
    assert dfm_.equals(dfm)


# TODO: implement tests
@pytest.mark.skip("Only a sceleton.")
def test_vintage():
    assert 0


# TODO: implement tests
@pytest.mark.skip("Only a sceleton.")
def test_collection():
    assert 0


def test_resulting_dataframes():
    assert dfa.GDP_bln_rub['1999-12-31'] == 4823.0


def test_resulting_dataframes_with_time_index():
    assert dfq.to_dict('list') == {
        'year': [
            1999, 1999, 1999, 1999, 2000, 2000, 2000, 2000], 'qtr': [
            1, 2, 3, 4, 1, 2, 3, 4], 'GDP_bln_rub': [
                901.0, 1102.0, 1373.0, 1447.0, 1527.0, 1697.0, 2038.0, 2044.0]}


def test_resulting_dataframes_no_dfm():
    assert dfm.empty is True


if __name__ == "__main__":
    pytest.main([__file__])
