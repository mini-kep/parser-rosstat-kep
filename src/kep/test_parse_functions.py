from datetime import date
import pandas as pd
import pytest

import parse

# Testing statless functions

# risk areas: annual values were not similar to other freq 
#             class of timestamps
class Test_Functions_Dates():
    def test_quarter_end_returns_pd_Timestamp(self):
        assert parse.get_date_quarter_end(2015, 1) == \
               pd.Timestamp('2015-03-31 00:00:00')
        assert parse.get_date_quarter_end(2015, 4) == \
               pd.Timestamp('2015-12-31 00:00:00')
        assert parse.get_date_quarter_end(2015, 4) == \
               pd.Timestamp(date(2015, 4 * 3, 1)) + pd.offsets.QuarterEnd()

    def test_month_end_returns_pd_Timestamp(self):
        assert parse.get_date_month_end(2015, 8) == \
               pd.Timestamp('2015-08-31 00:00:00')
        assert parse.get_date_month_end(2015, 1) == \
               pd.Timestamp(date(2015, 1, 1)) + pd.offsets.MonthEnd()

    def test_year_end_returns_pd_Timestamp(self):
        assert parse.get_date_year_end(2015) == pd.Timestamp('2015-12-31 00:00:00')
        assert parse.get_date_year_end(2015) == \
               pd.Timestamp('2015') + pd.offsets.YearEnd()


# risk area: underscore as a separator may change
class Test_Functions_Label_Handling:
    def test_multiple_functions(self):
        assert parse.extract_unit("GDP_mln_rub") == "mln_rub"
        assert parse.extract_varname("GDP_mln_rub") == "GDP"
        assert parse.split_label("GDP_mln_rub") == ("GDP", "mln_rub")
        assert parse.make_label("GDP", "mln_rub") == "GDP_mln_rub"

class Test_Function_to_float:
    # risk area: may be None instead of False, to discuss
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert parse.to_float(x) is False

    def test_on_single_value_returns_float(self):
        assert parse.to_float('5.678,') == 5.678
        assert parse.to_float('5.678,,') == 5.678
        assert parse.to_float("5.6") == 5.6
        assert parse.to_float("5,6") == 5.6
        assert parse.to_float("5,67") == 5.67
        assert parse.to_float("5,67,") == 5.67

    def test_on_comments_returns_float(self):
        assert parse.to_float('123,0 4561)') == 123
        assert parse.to_float('6762,31)2)') == 6762.3
        assert parse.to_float('1734.4 1788.42)') == 1734.4

    def test_on_max_recursion_depth_throws_exception(self):
        with pytest.raises(ValueError):
            parse.to_float("1.2,,,,,")

    def test_on_all_values(self):
        for s in self.all_values():
            f = parse.to_float(s)
            assert isinstance(f, float) or f is False           

    @staticmethod 
    def all_values():
        """Emit all values for debugging to_float()"""
        import files
        csv_path = files.get_path_csv()
        for table in parse.Tables(csv_path).get_all():
            for row in table.datarows:
                for value in row.data:
                    yield value

class Test_Function_get_year():
    def test_get_year(self):
        assert parse.get_year("19991)") == 1999
        assert parse.get_year("1999") == 1999
        assert parse.get_year("1812") is None

    def test_on_all_heads(self):
        for s in self.all_heads():
            year = parse.get_year(s) 
            assert isinstance(year, int) or year is None                             

#FIXME: why to_float defaults to False and get_year to None? 
            
    @staticmethod 
    def all_heads():
        """Emit all heads for debugging get_year()"""
        import files
        csv_path = files.get_path_csv()
        csv_dicts = parse.read_csv(csv_path)
        for d in csv_dicts:
            yield d.name
                             

if __name__ == "__main__":
    pytest.main(['test_parse_functions.py'])                      