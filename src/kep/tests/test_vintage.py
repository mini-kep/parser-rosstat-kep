import pytest
import pandas as pd
import tempfile
from pathlib import Path

from kep import FREQUENCIES
from kep.vintage import Vintage


class Test_Vintage:
    
    def setup(self):
        self.vintage = Vintage(2017, 10)
        self.temp_folder = Path(tempfile.tempdir)
        def make_path(freq: str, year: str, month: str, root = self.temp_folder):
            return root / 'processed' / year / month / f'df{freq}.csv' 
        self.paths = [make_path(freq, '2017', '10') for freq in FREQUENCIES]
        # may have temp files form previous run, clean them up 
        self.teardown() 

    def test_init_results_in_dataframes_in_dfs_property(self):
        for freq in FREQUENCIES:
            df = self.vintage.dfs[freq]
            assert isinstance(df, pd.DataFrame)

    def test_repr_is_callable_and_returns_a_string(self):
        assert isinstance(repr(self.vintage), str)

    def test_save_writes_files_to_folder(self):
        # call
        self.vintage.save(folder=self.temp_folder)
        # check
        for f in self.paths:
            assert f.exists()
            assert f.stat().st_size > 0

    def teardown(self):
        for f in self.paths:
            if f.exists():
                f.unlink()

#EP: Latest removed in code

#class Test_Latest:
#    def test_init_on_very_old_date_raises_exception(self):
#        year, month = 2017, 10
#        with pytest.raises(ValueError, match=r'Operation cannot be completed .*'):
#            Latest(year, month)
#
#    # WARNING: the test will fail if no current pasring took place 
#    #          and files for recent month were not created 
#    def test_init_on_recent_date_creates_instance(self):
#        year, month = Date.latest_dates[0]
#        assert Latest(year, month)

if __name__ == "__main__":
    pytest.main([__file__])
