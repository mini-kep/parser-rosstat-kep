import pytest

from kep.helper.date import supported_dates


class Test_supported_dates():

    def test_supported_dates_starts_in_2009_4(self):
        assert supported_dates()[0] == (2009, 4)

    def test_supported_dates_excludes_2013_11(self):
        assert (2013, 11) not in supported_dates()

    def test_supported_dates_is_after_2017(self):
        assert supported_dates()[-1][0] >= 2017


if __name__ == "__main__":
    pytest.main([__file__])
