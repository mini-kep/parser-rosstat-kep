import pytest
import arrow

from kep.helper.path import (UNPACK_RAR_EXE, XL_PATH,
                             DataFolder,
                             InterimCSV, ProcessedCSV,
                             LocalRarFile,
                             )


def test_csv_has_no_null_byte():
    csv_path = InterimCSV(2015, 2).path
    z = csv_path.read_text(encoding='utf-8')
    assert "\0" not in z

def test_constants():
    assert isinstance(UNPACK_RAR_EXE, str)
    assert isinstance(XL_PATH, str)


# TODO: randomise tests with a random pair from supported dates
class Test_DataFolder():

    # we assume for (2015, 5) all folders exist

    def test_repr_method_is_callable(self):
        assert repr(DataFolder(2015, 5))

    # FIXME: three tests below can be parametrised using the property names
    # >>> DataFolder(2015,1).raw
    # WindowsPath('c:/Users/PogrebnyakEV/Desktop/mini-kep/kep/data/raw/2015/01')
    # >>> DataFolder(2015,1).interim
    # WindowsPath('c:/Users/PogrebnyakEV/Desktop/mini-kep/kep/data/interim/2015/01')
    # >>> DataFolder(2015,1).processed
    # WindowsPath('c:/Users/PogrebnyakEV/Desktop/mini-kep/kep/data/processed/2015/01')
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
            year = arrow.now().year + 1
            DataFolder(year, 1)


class Test_LocalRarFile():
    path = LocalRarFile(2015, 5).path

    def test_on_init_path_property_is_Path_class_instance(self):
        assert isinstance(self.path, str)

    def test_on_init_path_name_is_as_expected(self):
        assert self.path.endswith('ind.rar')


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

    def test_path_method_fails_on_literal_outside_aqm(self):
        with pytest.raises(ValueError):
            ProcessedCSV(2015, 5).path('x')


if __name__ == "__main__":
    pytest.main([__file__])
