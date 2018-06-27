import pytest

from util.date import supported_dates, is_latest


class Test_supported_dates():
     
     supported = supported_dates()
    
     def test_supported_starts_in_2009_4(self):
        assert self.supported[0] == (2009, 4)

     def test_supported_excludes_2013_11(self):
        assert (2013, 11) not in self.supported

     def test_supported_is_after_2017(self):
        assert self.supported[-1][0] >= 2017   
    

       
def test_is_latest():
    year, month = supported_dates()[-1]
    #year ago
    year -= 1
    assert is_latest(year, month ) is False       


if __name__ == "__main__":
    pytest.main([__file__])
