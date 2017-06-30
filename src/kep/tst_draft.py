"""
Current coverage report:

Name          Stmts   Miss  Cover   Missing
-------------------------------------------
cfg.py          134     15    89%   80, 83-84, 100-104, 107, 262-267

files.py         67     19    72%   50, 77-83, 108-109, 127, 132-136, 140-142

parse.py        413     45    89%   55-59, 137, 157, 175-176, 179-184, 288-291,
383, 399, 434, 446, 481, 540, 572-575, 603-604, 608, 614, 619, 629-630, 635-636, 643-645, 652-656

splitter.py      30     10    67%   35, 54, 65, 69-71, 83-84, 116-117
-------------------------------------------
TOTAL           644     89    86%

General Notes:

    To achieve maximum coverage "sad paths" should be tested as well as "happy paths"

    Related tests should be grouped in a TestClass as it makes tests more readable,
    grouped meaningfully and one can easily notice if tests are missing or duplicated.

    Mocks should be used to test each entity in isolation from its dependencies

splitter.py:
    this are mostly stateless functions and can be tested with traditional
    "give input expect output approach".

files.py:

    As far as the coverage report shows it is tested fairly well
    5 or 6 tests and it will be covered 100%. Tests missing for:
        - filter_date sad path
        - init_dirs
        - InterimDataFolder.get_latest_folder
        - etc.
    Maybe some refactoring (grouping of tests etc.)

parse.py:
    following are the test skeletons for parse module
    first of all existing tests should be split and added in appropriate stub methods
    Then remaining stubs should be implemented. Tests should be added or removed accordingly,
    during implementation.
"""


# label handling tests
class TestLabelHandling(object):
    def test_make_label(self):
        pass

    def test_split_label(self):
        pass

    def test_extract_varname(self):
        pass

    def extract_unit(self):
        pass


# csv file access tests
class TestCsvFileAccess(object):
    def test_to_csv(self):
        pass

    def test_from_csv(self):
        pass

    def test_read_csv(self):
        pass


class TestTables(object):
    def test_get_all_without_additional_definitions(self):
        pass

    def test_get_all_with_additional_definitions(self):
        pass

    def test_get_defined(self):
        pass


class TestYearFunctions(object):
    # Happy path
    def test_get_year_with_match(self):
        pass

    # Sad path
    def test_get_year_withouth_match(self):
        pass

    # Happy path
    def test_get_year_greater_or_equal_1991(self):
        pass

    # Sad path
    def test_get_year_less_than_1991(self):
        pass

    # Happy path
    def test_is_year_on_valid_year(self):
        pass

    # Sad path
    def test_is_year_on_invalid_year(self):
        pass


class TestRow(object):
    pass


class TestRowStack(object):
    def test_is_matched_on_empty_pat(self):
        pass

    # Happy path
    def test_is_matched_on_textline_starting_with_pat(self):
        pass

    # Sad path
    def test_is_matched_on_textline_not_starting_with_pat(self):
        pass

    def test_is_found_on_matching_text(self):
        pass

    def test_is_found_on_not_matching_text(self):
        pass

    # TODO: add some more test_pop_* functions to cover whole method
    def test_pop(self):
        pass

    # TODO: add some more test_pop_segment_* functions to cover whole method
    def test_pop_segment(self):
        pass


class TestSplitToTables(object):
    # TODO: add methods to cover split_to_tables method
    pass


class TestTable(object):
    # TODO: add methods to test parse.Table class
    pass


class TestHeader(object):
    # TODO: add methods to test parse.Header class
    pass


class TestFixMultiTableUnits(object):
    pass


class TestCheckRequiredLabels(object):
    pass


class TestGetTablesFromRowsSegment(object):
    pass


class TestToFloat(object):
    pass


class TestDictMaker(object):
    pass


class TestEmitter(object):
    pass


class TestDatapoints(object):
    pass


class TestDataframeDatesHandling(object):
    def test_month_end_day(self):
        pass

    def test_get_date_month_end(self):
        pass

    def test_get_date_quarter_end(self):
        pass

    def test_get_date_year_end(self):
        pass


class TestFrames(object):
    pass


# This will probably be integration test of all the previously defined entities
class TestVintage(object):
    pass


class TestCollection(object):
    pass
