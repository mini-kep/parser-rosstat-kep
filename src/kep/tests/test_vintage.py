import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path


from kep import FREQUENCIES
from kep.vintage import Vintage


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
    def  test_init_results_in_dataframe(self):
        for freq in FREQUENCIES:
            df=self.vintage.dfs[freq]
            assert isinstance(df, pd.DataFrame)

    def test_repr_is_callable_and_returns_a_string(self):
        # EP: just make sure it is callable + type check
        #     is there is an error in repr it ususally fails very silently
        assert isinstance(repr(self.vintage), str)

    def test_save(self):         
        # setup
        year, month = 2017, 10       
        temp_folder = Path(tempfile.tempdir)
        v = Vintage(year, month)
        # call
        # EP: we now have an option to infect a directory to .save()
        v.save(folder = temp_folder)
        # check
        filenames = [f'df{freq}.csv' for freq in FREQUENCIES]
        folder = temp_folder / 'processed' / '2017' / '10'
        files = [ folder / fn for fn in filenames]
        for f in files:
            assert f.exists()
            assert f.stat().st_size > 0
            # cleanup
            f.unlink() 
    


    # def test_save_files_exist(self):
    #     path_ = (Folders.processed / "2017" / "10")
    #     if path_.exists():
    #         shutil.rmtree(str(path_))

    #     year, month = 2017, 10
    #     vintage = Vintage(year, month)
    #     vintage.save()

    #     assert path_.exists()
    #     for freq in FREQUENCIES:
    #         assert ((path_ / "df{}.csv".format(freq)).exists())

