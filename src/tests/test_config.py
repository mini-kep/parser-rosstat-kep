import pytest

from config import (find_repo_root, supported_dates,
                    DataFolder, LocalCSV,
                    Latest, get_latest_date)


#HS: tests for the supported_dates combined in a class 
class Test_supported_dates(): 
    
    def test_supported_dates_starts_in_2009_4(self):
        assert supported_dates()[0] == (2009, 4)

    def test_supported_dates_excludes_2013_11(self):
        assert (2013, 11) not in supported_dates()

# WONTFIX: The supported_dates() finishes with the current date,
#          while the data in 'data/interim' is up to 10.2017.
#          the problem may be related to https://github.com/mini-kep/parser-rosstat-kep/issues/110 
# Skip the test until the problem is resolved.      
@pytest.mark.skip(reason="The data after 10.2017 is not available")
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
        raw_folder = DataFolder(2015, 5).raw
        assert raw_folder.exists()
    
    def test_get_interim_property_method_returns_existing_folder(self):
        interim_folder = DataFolder(2015, 5).interim 
        assert interim_folder.exists()
    
    def test_get_processed_property_method_returns_existing_folder(self):
        processed_folder = DataFolder(2015, 5).processed
        assert processed_folder.exists()

    def test_out_of_range_year_does_raises_error(self):
        with pytest.raises(ValueError):
            DataFolder(2018, 1)

class Test_LocalCSV():
    def test_get_interim_property_method_returns_existing_file(self):
        interim_csv = LocalCSV(2015, 5).interim 
        assert interim_csv.exists()

    def test_get_interim_property_method_returns_tab_csv(self):
        interim_csv = LocalCSV(2015, 5).interim
        expected_name = 'tab.csv'
        assert interim_csv.name == expected_name

    def test_processed_method_returns_existing_files(self):
        for freq in 'aqm':
            processed_csv = LocalCSV(2015, 5).processed(freq) 
            assert processed_csv.exists()

    def test_processed_method_returns_df_a_q_m_csv(self):
        for freq in 'aqm':
            expected_name = 'df{}.csv'.format(freq)
            processed_csv = LocalCSV(2015, 5).processed(freq) 
            assert processed_csv.name == expected_name


class Test_Latest():
    def test_csv_method_returns_existing_files(self):
        for freq in 'aqm':
            Latest_csv = Latest.csv(freq)
            assert Latest_csv.exists()

    def test_csv_method_returns_df_a_q_m_csv(self):
        for freq in 'aqm':
            expected_name = 'df{}.csv'.format(freq)
            Latest_csv = Latest.csv(freq)
            assert Latest_csv.name == expected_name


if __name__ == "__main__":
    pytest.main([__file__])
