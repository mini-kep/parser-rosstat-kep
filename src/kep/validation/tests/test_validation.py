import pytest

from kep.vintage import Vintage
from kep.validation.checkpoints import (
    validate2,
    Checkpoint,
    ValidationError,
    find_missed_checkpoints,
    find_uncovered_column_names
)


@pytest.fixture(scope="module")
def dataframe():
    return Vintage(2017, 12).dfs["a"]


@pytest.fixture(scope="module")
def upfront_absent_checkpoints():
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


def test_validate_raises_value_error_on_missed_checkpoint_in_dataframe(dataframe, upfront_absent_checkpoints):
    with pytest.raises(ValidationError):
        validate2(dataframe, upfront_absent_checkpoints, [])


def test_validate_returns_without_error_on_good_path(dataframe, good_path_checkpoints):
    validate2(dataframe, good_path_checkpoints, [])


def test_validate_raises_value_error_on_uncovered_checkpoint_in_dataframe(dataframe, good_path_checkpoints):
    with pytest.raises(ValidationError):
        validate2(dataframe, good_path_checkpoints, good_path_checkpoints, strict=True)


def test_find_missed_checkpoints_returns_missed_checkpoints(dataframe, upfront_absent_checkpoints):
    assert find_missed_checkpoints(dataframe, upfront_absent_checkpoints) == set(upfront_absent_checkpoints)


def test_find_missed_checkpoints_returns_empty_set_on_valid_data(dataframe, good_path_checkpoints):
    assert find_missed_checkpoints(dataframe, good_path_checkpoints) == set()


def test_find_uncovered_column_names_returns_valid_data(dataframe, upfront_absent_checkpoints, good_path_checkpoints):
    assert len(find_uncovered_column_names(dataframe, [])) == len(dataframe.columns)
    assert len(find_uncovered_column_names(dataframe, upfront_absent_checkpoints)) == len(dataframe.columns)
    assert len(find_uncovered_column_names(dataframe, good_path_checkpoints)) == \
        len(dataframe.columns) - len(good_path_checkpoints)
