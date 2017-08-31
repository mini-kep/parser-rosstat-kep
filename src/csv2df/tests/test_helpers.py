# -*- coding: utf-8 -*-
import pytest
import datetime as dt
from csv2df.helpers import PathHelper, DateHelper

year, month = DateHelper.get_latest_date()


class Test_PathHelper:

    def test_locate_csv_on_year_month_path_esists(self):
        assert PathHelper.locate_csv(2017, 5).exists() is True

    def test_locate_csv_on_noarg_works_and_retruns_path_that_esists(self):
        assert PathHelper.locate_csv().exists() is True

    def test_get_processed_folder_returns_existing_folder(self):
        assert PathHelper.get_processed_folder(2017, 5).exists() is True

    def test_get_processed_folder_will_not_work_without_arguments(self):
        with pytest.raises(TypeError):
            PathHelper.get_processed_folder()


class Test_DateHelper:

    def test_filled_dates_runs_on_Nones(self):
        assert DateHelper.filter_date(
            None, None) == DateHelper.get_latest_date()

    def test_filled_dates_runs_on_year_month(self):
        assert DateHelper.filter_date(2017, 5) == (2017, 5)

    def test_get_supported_dates_starts_in_2009_4(self):
        assert DateHelper.get_supported_dates()[0] == (2009, 4)

    def test_get_supported_dates_ends_with_latest_date(self):
        prev_month_date = dt.datetime.today().replace(day=1) - dt.timedelta(days=1)
        assert DateHelper.get_supported_dates()[-1] == (prev_month_date.year,
                                                        prev_month_date.month)

    def test_get_supported_dates_excludes_2013_11(self):
        assert (2013, 11) not in DateHelper.get_supported_dates()

    def test_get_latest_date(self):
        year, month = DateHelper.get_latest_date()
        assert year >= 2017
        assert month >= 1
        assert month <= 12


@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_init_dirs():
    assert False


if __name__ == "__main__":
    pytest.main([__file__])
