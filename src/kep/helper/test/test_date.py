import pytest

from kep.helper.date import Date, supported_dates


class Test_supported_dates():
     
     supported = supported_dates()
    
     def test_supported_starts_in_2009_4(self):
        assert self.supported[0] == (2009, 4)

     def test_supported_excludes_2013_11(self):
        assert (2013, 11) not in self.supported

     def test_supported_is_after_2017(self):
        assert self.supported[-1][0] >= 2017   
    

       
class Test_Date():
    def test_init_on_supported_passes(self):
        assert Date(2017, 12).year == 2017
        assert Date(2017, 12).month == 12

    def test_assert_supported(self):
        with pytest.raises(ValueError):        
            assert Date(1960, 12).assert_supported()

    def test_is_latest_date(self):
        year, month = Date.supported_dates[-1]
        year -= 1
        assert Date(year, month).is_latest() is False

    def test_assert_latest_date(self):
        year, month = Date.supported_dates[-1]
        year -= 1
        with pytest.raises(ValueError):
            Date(year, month).assert_latest()
        


if __name__ == "__main__":
    pytest.main([__file__])
