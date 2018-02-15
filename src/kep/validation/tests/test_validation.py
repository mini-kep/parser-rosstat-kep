import pytest

from kep.vintage import Vintage
from kep.validation.checkpoints import validate2, Checkpoint


@pytest.fixture(scope="module")
def dataframe():
    return Vintage(2017, 12).dfs["a"]

# TODO: this is 'bad path' checkpoints, need a fixture + test with 'good path' checkpoints 
@pytest.fixture(scope="module")
def checkpoints():
    return [
        Checkpoint(
            date="1999",
            freq ="z"
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

 # TODO: need simplest tests touching  
 # def find_missed_checkpoints(df, checkpoints):
 # def find_uncovered_column_names(df, checkpoints):        
