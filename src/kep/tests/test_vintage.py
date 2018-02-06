import pytest

from kep.vintage import Vintage

# TODO: implement tests
@pytest.mark.skip("Only a sceleton.")
def test_vintage():
    assert 0


# TODO: implement tests
@pytest.mark.skip("Only a sceleton.")
def test_collection():
    assert 0


def test_vintage():
    year, month = 2017, 10
    vint = Vintage(year, month)
    vint.validate()