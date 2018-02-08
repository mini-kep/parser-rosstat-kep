import pytest

from kep.vintage import Vintage


def test_Vintage():
    year, month = 2017, 10
    vint = Vintage(year, month)
    vint.validate()
    vint.save()
