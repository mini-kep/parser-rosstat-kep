from datetime import date
import pandas as pd
import pytest

import kep.tables as tables
import kep.vintage as vintage


# Testing statless functions

class Test_Function_to_float:
    # risk area: may be None instead of False, to discuss
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert vintage.to_float(x) is False

    def test_on_single_value_returns_float(self):
        assert vintage.to_float('5.678,') == 5.678
        assert vintage.to_float('5.678,,') == 5.678
        assert vintage.to_float("5.6") == 5.6
        assert vintage.to_float("5,6") == 5.6
        assert vintage.to_float("5,67") == 5.67
        assert vintage.to_float("5,67,") == 5.67

    def test_on_comments_returns_float(self):
        assert vintage.to_float('123,0 4561)') == 123
        assert vintage.to_float('6762,31)2)') == 6762.3
        assert vintage.to_float('1734.4 1788.42)') == 1734.4

    def test_on_max_recursion_depth_throws_exception(self):
        with pytest.raises(ValueError):
            vintage.to_float("1.2,,,,,")

    # FIXME:
    #def test_on_all_values(self):
    #    for s in self.all_values():
    #        f = vintage.to_float(s)
    #        assert isinstance(f, float) or f is False

    @staticmethod
    def all_values():
        """Emit all values for debugging to_float()"""
        import files
        csv_path = files.get_path_csv()
        for table in tables.Tables(csv_path).tables:
            for row in table.datarows:
                for value in row.data:
                    yield value


class Test_Functions_Dates():
    def test_quarter_end_returns_pd_Timestamp(self):
        assert vintage.get_date_quarter_end(2015, 1) == \
            pd.Timestamp('2015-03-31 00:00:00')
        assert vintage.get_date_quarter_end(2015, 4) == \
            pd.Timestamp('2015-12-31 00:00:00')
        assert vintage.get_date_quarter_end(2015, 4) == \
            pd.Timestamp(date(2015, 4 * 3, 1)) + pd.offsets.QuarterEnd()

    def test_month_end_returns_pd_Timestamp(self):
        assert vintage.get_date_month_end(2015, 8) == \
            pd.Timestamp('2015-08-31 00:00:00')
        assert vintage.get_date_month_end(2015, 1) == \
            pd.Timestamp(date(2015, 1, 1)) + pd.offsets.MonthEnd()

    def test_year_end_returns_pd_Timestamp(self):
        assert vintage.get_date_year_end(
            2015) == pd.Timestamp('2015-12-31 00:00:00')
        assert vintage.get_date_year_end(2015) == \
            pd.Timestamp('2015') + pd.offsets.YearEnd()


if __name__ == "__main__":
    pytest.main([__file__])
