import pytest

from kep.vintage import Vintage
from kep.validation.checkpoints import (
    Annual,
    ValidationError,
    include,
    expect
)


@pytest.fixture(scope="module")
def dataframe():
    return Vintage(2017, 12).dfs["a"]


@pytest.fixture(scope="module")
def absent():
    return [
        Annual(
            date="1999",
            label="some_really_long_test_variable",
            value=100.0,
        )
    ]


@pytest.fixture(scope="module")
def present():
    return [
        Annual(
            date="1999",
            label="AGROPROD_yoy",
            value=103.8,
        )
    ]

class Test_verify():

    def test_raises_value_error_on_missed_points(self, dataframe, absent):
        with pytest.raises(ValidationError):
            include(dataframe, absent)    
    
    def test_returns_without_error_on_good_path(self, dataframe, present):
        include(dataframe, present)

    def test_expect_passed(self, dataframe, present, absent):
        expect(dataframe, present)
        expect(dataframe, absent)
    
