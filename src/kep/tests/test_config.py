import pytest

from kep.config import (DataFolder, InterimCSV, Latest, ProcessedCSV,
                        find_repo_root, get_latest_date, supported_dates)


class Test_supported_dates():

    def test_supported_dates_starts_in_2009_4(self):
        assert supported_dates()[0] == (2009, 4)

    def test_supported_dates_excludes_2013_11(self):
        assert (2013, 11) not in supported_dates()

    def test_supported_dates_is_after_2017(self):
        assert supported_dates()[-1][0] >= 2017

# Directory creation not tested
def test_md():
    pass

# =========================================================================================

# WONTFIX: The supported_dates() finishes with the current date,
#          while the data in 'data/interim' is up to 10.2017.
#          the problem may be related to https://github.com/mini-kep/parser-rosstat-kep/issues/110
#          We skip the test until the problem is resolved.
#@pytest.mark.skip(reason="The data after 10.2017 is not available")
# def test_supported_dates_ends_with_latest_date():
#    base_dir = find_repo_root()
#    latest_year, latest_month = get_latest_date(
#        base_dir / 'data' / 'interim')
#    assert supported_dates()[-1] == (latest_year, latest_month)


# FIXME: make class get_latest_date
def test_get_latest_date_returns_year_after_2017_and_month_in_1_12():
    base_dir = find_repo_root()
    year, month = get_latest_date(base_dir / 'data' / 'interim')
    assert year >= 2017
    assert 1 <= month <= 12


class Test_DataFolder():

    # we assume for (2015, 5) all folders exist

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


class Test_InterimCSV():
    def test_path_property_returns_existing_file(self):
        interim_csv = InterimCSV(2015, 5).path
        assert interim_csv.exists()

    def test_path_property_filename_is_tab_csv(self):
        interim_csv = InterimCSV(2015, 5).path
        expected_name = 'tab.csv'
        assert interim_csv.name == expected_name


class Test_ProcessedCSV():
    def test_path_method_returns_existing_files(self):
        for freq in 'aqm':
            processed_csv = ProcessedCSV(2015, 5).path(freq)
            assert processed_csv.exists()

    def test_path_method_returns_expected_filenames_df_a_q_m_csv(self):
        for freq in 'aqm':
            processed_csv = ProcessedCSV(2015, 5).path(freq)
            expected_name = 'df{}.csv'.format(freq)
            assert processed_csv.name == expected_name


# >>> DataFolder(2015,1).raw
# WindowsPath('c:/Users/PogrebnyakEV/Desktop/mini-kep/kep/data/raw/2015/01')
# >>> DataFolder(2015,1).interim
# WindowsPath('c:/Users/PogrebnyakEV/Desktop/mini-kep/kep/data/interim/2015/01')
# >>> DataFolder(2015,1).processed
# WindowsPath('c:/Users/PogrebnyakEV/Desktop/mini-kep/kep/data/processed/2015/01')


if __name__ == "__main__":
    pytest.main([__file__])
