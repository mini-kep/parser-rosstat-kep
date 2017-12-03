import pytest

# EP: is this used in test?
import datetime as dt

from config import (find_repo_root, supported_dates,
                    DataFolder, LocalCSV,
                    Latest, get_latest_date)


#HS: tests for the supported_dates added, the ones from 
#    the old DateHelper module removed
# FIXME: this can be combined in class Test_supported_dates 
def test_supported_dates_starts_in_2009_4():
    assert supported_dates()[0] == (2009, 4)

def test_supported_dates_excludes_2013_11():
    assert (2013, 11) not in supported_dates()

# WONTFIX: what is happening in this test, why is it skipped? should this test be deleted?      
#          the problem may be related to https://github.com/mini-kep/parser-rosstat-kep/issues/110 
@pytest.mark.skip(reason="The data ends with 10.2017")
def test_supported_dates_ends_with_latest_date():
    base_dir = find_repo_root()
    latest_year, latest_month = get_latest_date(base_dir / 'data' / 'interim')
    assert supported_dates()[-1] == (latest_year, latest_month)

# EP: brought up, renamed    
def test_get_latest_date_returns_year_after_2017_and_month_in_1_12():
    base_dir = find_repo_root()
    year, month = get_latest_date(base_dir / 'data' / 'interim')
    assert year >= 2017
    assert 1 <= month <= 12  
    

class Test_DataFolder():
    
    # we assume a typical state of repo for (2015, 5)      
    
    def test_repr_method_is_callable(self):
        assert repr(DataFolder(2015, 5))
    
    # WONTFIX: three tests below be parametrised 
    def test_get_raw_property_method_returns_existing_folder(self):
        # EP: this is a call of code under test
        raw_folder = DataFolder(2015, 5).raw
        # EP: this is a check, they should be separated accorting to guidelines
        assert raw_folder.exists()
    
    def test_get_interim_property_method_returns_existing_folder(self):
        interim_folder = DataFolder(2015, 5).interim 
        assert interim_folder.exists()
    
    def test_get_processed_property_method_returns_existing_folder(self):
        processed_folder = DataFolder(2015, 5).processed
        assert processed_folder.exists()

    def test_out_of_range_year_does_raises_error(self):
        with pytest.raises(ValueError):
            # EP: slightly better with current year + 1
            DataFolder(2088, 1)

class Test_LocalCSV():
    def test_get_interim_property_method_returns_existing_file(self):
        interim_csv = LocalCSV(2015, 5).interim 
        assert interim_csv.exists()

    def test_processed_method_returns_existing_files(self):
        for freq in 'aqm':
            processed_csv = LocalCSV(2015, 5).processed(freq) 
            assert processed_csv.exists()

    # FIMXE: can also check interim and process file names        

class Test_Latest():
    def test_csv_method_returns_existing_files(self):
        for freq in 'aqm':
            assert Latest.csv(freq).exists()

if __name__ == "__main__":
    pytest.main([__file__])
