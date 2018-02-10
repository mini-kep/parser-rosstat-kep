import pytest
import pandas as pd
import tempfile
from pathlib import Path

from kep import FREQUENCIES
from kep.vintage import Vintage, Latest
from kep.helper.date import supported_dates


def test_Vintage():
    year, month = 2017, 10
    vint = Vintage(year, month)
    vint.validate()
    vint.save()


class Test_Vintage():
    year, month = 2017, 10
    vintage = Vintage(year, month)

    # EP: on init Vintage does a great deal of work of creating dataframes
    #     this is a VERY important part to check!
    def test_init_results_in_dataframe(self):
        for freq in FREQUENCIES:
            df = self.vintage.dfs[freq]
            assert isinstance(df, pd.DataFrame)

    def test_repr_is_callable_and_returns_a_string(self):
        # EP: just make sure it is callable + type check
        #     is there is an error in repr it ususally fails very silently
        assert isinstance(repr(self.vintage), str)


class Test_Vintage_save:
    def setup(self):
        self.temp_folder = Path(tempfile.tempdir)
        filenames = [f'df{freq}.csv' for freq in FREQUENCIES]
        folder = self.temp_folder / 'processed' / '2017' / '10'
        self.files = [folder / fn for fn in filenames]

    def test_save(self):
        year, month = 2017, 10
        v = Vintage(year, month)
        # call
        # EP: we now have an option to inject a directory to .save()
        v.save(folder=self.temp_folder)
        # check
        for f in self.files:
            assert f.exists()
            assert f.stat().st_size > 0

    def teardown(self):
        for f in self.files:
            f.unlink()


def test_latest_vintage_raises_exception_on_too_old_date():
    year, month = 2017, 10
    with pytest.raises(ValueError, match=r'Operation cannot be completed .*'):
        Latest(year, month)


def test_latest_vintage_creation_with_recent_date():
    year, month = supported_dates()[-2]
    assert Latest(year, month)


if __name__ == "__main__":
    pytest.main([__file__])
