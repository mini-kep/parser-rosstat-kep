# -*- coding: utf-8 -*-
import pytest
import datetime as dt

from config import DataFolder
from config import LocalCSV
from config import supported_dates
from config import Latest
from config import get_latest_date
from config import find_repo_root


@pytest.mark.skip()
def test_md(folder):
    assert False

@pytest.mark.skip()
def test_md(folder):
    assert False


@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_copy_latest():
    assert False

@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_init_dirs():
    assert False

#HS: tests for the property methods added, instead of get_ functions
class Test_DataFolder():
    
    # we assume a typical state of repo for (2015, 5)      
    
    def test_repr(self):
        assert repr(DataFolder(2015, 5))

    def test_get_raw_property_method_returns_existing_folder(self):
        assert DataFolder(2015, 5).raw.exists()
    
    def test_get_interim_property_method_returns_existing_folder(self):
        assert DataFolder(2015, 5).interim.exists()
    
    def test_get_processed_property_method_returns_existing_folder(self):
        assert DataFolder(2015, 5).processed.exists()

    def test_out_of_range_year_does_raises_error(self):
        with pytest.raises(ValueError):
            DataFolder(2030, 1)

#HS: tests for the processed method for freqs 'a', 'q', 'm' added
class Test_LocalCSV():
    def test_get_interim_property_method_returns_existing_file(self):
        assert LocalCSV(2015, 5).interim.exists()

    def test_processed_method_returns_existing_files(self):
        for freq in 'aqm':
            assert LocalCSV(2015, 5).processed(freq).exists()

# skipping
@pytest.mark.skip(reason="not testing maintenance scripts")
def test_copy_latest():
    assert False

#HS: A test for the csv method of the Latest class is added
class Test_Latest():
    def test_csv_method_returns_existing_files(self):
        for freq in 'aqm':
            assert Latest.csv(freq).exists()

#HS: a test for the get_latest_date added
def test_get_latest_date_asserts_if_latest_date_earlier_than_2017():
    base_dir = find_repo_root()
    year, month = get_latest_date(base_dir / 'data/interim')
    assert year >= 2017

#HS: tests for the supported_dates added, the ones from 
#    the old DateHelper module removed
def test_supported_dates_starts_in_2009_4():
    assert supported_dates()[0] == (2009, 4)

def test_supported_dates_excludes_2013_11():
    assert (2013, 11) not in supported_dates()

@pytest.mark.skip(reason="The data ends with 10.2017")
def test_supported_dates_ends_with_latest_date():
    base_dir = find_repo_root()
    latest_year, latest_month = get_latest_date(base_dir / 'data/interim')
    assert supported_dates()[-1] == (latest_year, latest_month)



@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_init_dirs():
    assert False


if __name__ == "__main__":
    pytest.main([__file__])
