import pytest

from kep.vintage import Vintage
from kep.validation.checkpoints import (
    validate2,
    ValidationError,
    find_missed_checkpoints,
    find_uncovered_column_names
)


@pytest.fixture(scope="module")
def dataframe():
    return Vintage(2017, 12).dfs["a"]


@pytest.fixture(scope="module")
def upfront_absent_dicts():
    return [
        dict(
            date="1999",
            freq="z",
            name="some_really_long_test_variable",
            value=100.0,
        )
    ]


@pytest.fixture(scope="module")
def good_path_dicts():
    return [
        dict(
            date="1999",
            freq="a",
            name="AGROPROD_yoy",
            value=103.8,
        )
    ]


def test_validate_raises_value_error_on_missed_dict_in_dataframe(dataframe, upfront_absent_dicts):
    with pytest.raises(ValidationError):
        validate2(dataframe, upfront_absent_dicts, [])


def test_validate_returns_without_error_on_good_path(dataframe, good_path_dicts):
    validate2(dataframe, good_path_dicts, [])


def test_validate_raises_value_error_on_uncovered_dict_in_dataframe(dataframe, good_path_dicts):
    with pytest.raises(ValidationError):
        validate2(dataframe, good_path_dicts, good_path_dicts, strict=True)


def test_find_missed_checkpoints_returns_missed_dicts(dataframe, upfront_absent_dicts):
    assert find_missed_checkpoints(dataframe, upfront_absent_dicts) == set(upfront_absent_dicts)


def test_find_missed_checkpoints_returns_empty_set_on_valid_data(dataframe, good_path_dicts):
    assert find_missed_checkpoints(dataframe, good_path_dicts) == set()


def test_find_uncovered_column_names_returns_valid_data(dataframe, upfront_absent_dicts, good_path_dicts):
    assert len(find_uncovered_column_names(dataframe, [])) == len(dataframe.columns)
    assert len(find_uncovered_column_names(dataframe, upfront_absent_dicts)) == len(dataframe.columns)
    assert len(find_uncovered_column_names(dataframe, good_path_dicts)) == \
        len(dataframe.columns) - len(good_path_dicts)
