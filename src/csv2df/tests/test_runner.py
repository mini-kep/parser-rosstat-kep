import pytest

import io

from csv2df.specification import Definition, Specification
from csv2df.reader import Reader
from csv2df.parser import extract_tables
from csv2df.runner import Emitter, get_dataframes


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
    dfa_, dfq_, dfm_ = get_dataframes(csvfile1, spec1)
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

    assert dfq.to_string() == \
        """            year  qtr  GDP_bln_rub
1999-03-31  1999    1        901.0
1999-06-30  1999    2       1102.0
1999-09-30  1999    3       1373.0
1999-12-31  1999    4       1447.0
2000-03-31  2000    1       1527.0
2000-06-30  2000    2       1697.0
2000-09-30  2000    3       2038.0
2000-12-31  2000    4       2044.0"""

    assert dfm.empty is True


if __name__ == "__main__":
    pytest.main([__file__])
