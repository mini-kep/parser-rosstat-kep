import pytest

from kep.vintage import Vintage
from kep.validation.checkpoints import validate2, Checkpoint


@pytest.fixture(scope="module")
def dataframe():
    return Vintage(2017, 12).dfs["a"]


@pytest.fixture(scope="module")
def checkpoints():
    return [
        Checkpoint(
            date="1999",
            name="some_really_long_test_variable",
            value="100.0"
        )
    ]


def test_validate_raises_value_error_on_missed_checkpoint_in_dataframe(dataframe, checkpoints):
    with pytest.raises(ValueError):
        validate2(dataframe, checkpoints, [])


def test_validate_raises_value_error_on_uncovered_checkpoint_in_dataframe(dataframe):
    with pytest.raises(ValueError):
        validate2(dataframe, [], [])
