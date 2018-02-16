import pytest

from kep.vintage import Vintage
from kep.validation.checkpoints import validate2, Checkpoint, ValidationError


@pytest.fixture(scope="module")
def dataframe():
    return Vintage(2017, 12).dfs["a"]


@pytest.fixture(scope="module")
def bad_path_checkpoints():
    return [
        Checkpoint(
            date="1999",
            freq="z",
            name="some_really_long_test_variable",
            value=100.0,
        )
    ]


@pytest.fixture(scope="module")
def good_path_checkpoints():
    return [
        Checkpoint(
            date="1999",
            freq="a",
            name="AGROPROD_yoy",
            value=103.8,
        )
    ]


def test_validate_raises_value_error_on_missed_checkpoint_in_dataframe(dataframe, bad_path_checkpoints):
    with pytest.raises(ValidationError):
        validate2(dataframe, bad_path_checkpoints, [])


def test_validate_good_path(dataframe, good_path_checkpoints):
    validate2(dataframe, good_path_checkpoints, [])


def test_validate_raises_value_error_on_uncovered_checkpoint_in_dataframe(dataframe, good_path_checkpoints):
    with pytest.raises(ValidationError):
        validate2(dataframe, good_path_checkpoints, good_path_checkpoints, strict=True)

 # TODO: need simplest tests touching  
 # def find_missed_checkpoints(df, checkpoints):
 # def find_uncovered_column_names(df, checkpoints):        
