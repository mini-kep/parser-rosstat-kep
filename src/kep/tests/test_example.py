from kep.main import random_date, get_dataframes


def test_randomised_import():
    year, month = random_date()
    dfa, dfq, dfm = get_dataframes(year, month)
    assert not dfa.empty
    assert not dfq.empty
    assert not dfm.empty
