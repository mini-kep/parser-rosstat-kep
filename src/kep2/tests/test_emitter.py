from datetime import date
import pandas as pd
import pytest

import kep2.parcer as parcer
import kep2.emitter as emitter


# stateless functions

class Test_Function_to_float_on_values:
    # risk area: may be None instead of False, to discuss
    def test_on_invalid_characters_returns_False(self):
        for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
            assert emitter.to_float(x) is False

    def test_on_single_value_returns_float(self):
        assert emitter.to_float('5.678,') == 5.678
        assert emitter.to_float('5.678,,') == 5.678
        assert emitter.to_float("5.6") == 5.6
        assert emitter.to_float("5,6") == 5.6
        assert emitter.to_float("5,67") == 5.67
        assert emitter.to_float("5,67,") == 5.67

    def test_on_comments_returns_float(self):
        assert emitter.to_float('123,0 4561)') == 123
        assert emitter.to_float('6762,31)2)') == 6762.3
        assert emitter.to_float('1734.4 1788.42)') == 1734.4

    def test_on_max_recursion_depth_throws_exception(self):
        with pytest.raises(ValueError):
            emitter.to_float("1.2,,,,,")


# FIXME: difficult to maintain 
#
#class Test_Function_to_float_on_everything:
#    
#    @pytest.mark.skip("may try to run to float on actual data")
#    def test_all(self):
#    assert False
#
#    @staticmethod
#    def all_values():
#        """Emit all values for debugging to_float()"""
#        from kep2.reader import Reader
#        ...       
#        
#        parsing_inputs = Reader(csvfile, spec).items()
#        tables = get_tables(parsing_inputs)
#        csv_path = files.get_path_csv()
#        for table in tables.Tables(csv_path).tables:
#            for row in table.datarows:
#                for value in row.data:
#                    yield value


class Test_Functions_Dates():
#def get_date_month_end(year, month):
#    day = _month_end_day(year, month)
#    return pd.Timestamp(date(year, month, day))
#
#
#def get_date_quarter_end(year, qtr):
#    # quarter number should be based at 1
#    assert qtr <= 4 and qtr >= 1
#    month = qtr * 3
#    return get_date_month_end(year, month)
#
#
#def get_date_year_end(year):
#    return pd.Timestamp(date(year, 12, 31))

    def test_month_end_returns_pd_Timestamp(self):
        assert emitter.get_date_month_end(2015, 8) == \
            pd.Timestamp('2015-08-31')
        # offsets usage example       
        assert emitter.get_date_month_end(2015, 1) == \
            pd.Timestamp(date(2015, 1, 1)) + pd.offsets.MonthEnd()

    def test_quarter_end_returns_pd_Timestamp(self):
        assert emitter.get_date_quarter_end(2015, 1) == \
            pd.Timestamp('2015-03-31')
        assert emitter.get_date_quarter_end(2015, 4) == \
            pd.Timestamp('2015-12-31')
        # offsets usage example    
        assert emitter.get_date_quarter_end(2015, 4) == \
            pd.Timestamp(date(2015, 4 * 3, 1)) + pd.offsets.QuarterEnd()

    def test_year_end_returns_pd_Timestamp(self):
        assert emitter.get_date_year_end(2015) == pd.Timestamp('2015-12-31')
        # offsets usage example   
        assert emitter.get_date_year_end(2015) == \
            pd.Timestamp('2015') + pd.offsets.YearEnd()


class Test_DictMaker:
    
    @pytest.mark.skip("not implemented yet")
    def test_(self):
        assert False
        
class Test_Emitter:
    
    @pytest.mark.skip("not implemented yet")
    def test_(self):
        assert False

if __name__ == "__main__":
    pytest.main([__file__])

#COMMENT_CATCHER = re.compile("\D*(\d+[.,]?\d*)\s*(?=\d\))")
#
#
#def to_float(text, i=0):
#    i += 1
#    if i > 5:
#        raise ValueError("Max recursion depth exceeded on '{}'".format(text))
#    if not text:
#        return False
#    text = text.replace(",", ".")
#    try:
#        return float(text)
#    except ValueError:
#        # note: order of checks important
#        if " " in text.strip():  # get first value '542,0 5881)'
#            return to_float(text.strip().split(" ")[0], i)
#        if ")" in text:  # catch '542,01)'
#            match_result = COMMENT_CATCHER.match(text)
#            if match_result:
#                text = match_result.group(0)
#                return to_float(text, i)
#        if text.endswith(".") or text.endswith(","):  # catch 97.1,
#            return to_float(text[:-1], i)
#        return False
#
#
#class DictMaker:
#    def __init__(self, year, label):
#        self.basedict = {'year': year, 'label': label}
#
#    def a_dict(self, val):
#        return {**self.basedict, 'freq': 'a', 'value': to_float(val)}
#
#    def q_dict(self, val, q):
#        return {**self.basedict, 'freq': 'q', 'value': to_float(val), 'qtr': q}
#
#    def m_dict(self, val, m):
#        return {
#            **self.basedict,
#            'freq': 'm',
#            'value': to_float(val),
#            'month': m}
#
#    def __str__(self):
#        return self.basedict.__str__()
#
#
## dataframe dates handling
#
#def _month_end_day(year, month):
#    return calendar.monthrange(year, month)[1]
#
#
#def get_date_month_end(year, month):
#    day = _month_end_day(year, month)
#    return pd.Timestamp(date(year, month, day))
#
#
#def get_date_quarter_end(year, qtr):
#    # quarter number should be based at 1
#    assert qtr <= 4 and qtr >= 1
#    month = qtr * 3
#    return get_date_month_end(year, month)
#
#
#def get_date_year_end(year):
#    return pd.Timestamp(date(year, 12, 31))
#
#
#class Emitter:
#    """Emitter extractsand emits annual, quarterly and monthly values
#       from a list Table() instances.
#
#       Methods:
#           .get_dataframe(freq)
#
#       Raises:
#           ValueError if any table in list is not defined.
#
#       Method:
#           get_dataframe(freq)
#    """
#
#    def __init__(self, tables):
#        self.a = []
#        self.q = []
#        self.m = []
#        for t in tables:
#            self._add_table(t)
#
#    def _add_table(self, table):
#        if not table.is_defined():
#            raise ValueError("Undefined table:\n{}".format(table))
#        for row in table.datarows:
#            dmaker = DictMaker(row.get_year(), table.label)
#            a_value, q_values, m_values = table.splitter_func(row.data)
#            if a_value:
#                self.a.append(dmaker.a_dict(a_value))
#            if q_values:
#                qs = [dmaker.q_dict(val, t + 1)
#                      for t, val in enumerate(q_values) if val]
#                self.q.extend(qs)
#            if m_values:
#                ms = [dmaker.m_dict(val, t + 1)
#                      for t, val in enumerate(m_values) if val]
#                self.m.extend(ms)
#
#    def _collect(self, freq):
#        if freq in "aqm":
#            return dict(a=self.a, q=self.q, m=self.m)[freq]
#        else:
#            raise ValueError(freq)
#
#    @staticmethod
#    def _assert_has_no_duplicate_rows(df):
#        if df.empty:
#            dups = df
#        else:
#            dups = df[df.duplicated(keep=False)]
#        if not dups.empty:           #
#            raise ValueError("Duplicate rows found {}".format(dups))
#
#    def get_dataframe(self, freq):
#        df = pd.DataFrame(self._collect(freq))
#        if df.empty:
#            return pd.DataFrame()
#        self._assert_has_no_duplicate_rows(df)
#        # make time index
#        funcs = dict(a=lambda x: get_date_year_end(x['year']),
#                     q=lambda x: get_date_quarter_end(x['year'], x['qtr']),
#                     m=lambda x: get_date_month_end(x['year'], x['month']))
#        df["time_index"] = df.apply(funcs[freq], axis=1)
#        # reshape
#        df = df.pivot(columns='label', values='value', index='time_index')
#        # add yeay and period
#        df.insert(0, "year", df.index.year)
#        if freq == "q":
#            df.insert(1, "qtr", df.index.quarter)
#        elif freq == "m":
#            df.insert(1, "month", df.index.month)
#        # delete some df internals for better view
#        df.columns.name = None
#        df.index.name = None
#        return df
