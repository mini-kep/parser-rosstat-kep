from kep.utilities import TempFile
from kep.engine.reader import read_tables, read_csv, Table, split_csv

DOC = ("заголовок1 header1\t\t\t\n"
       "заголовок2 header2\t\t\t\n"
       "\t\tI\tII\tIII\tIV\n"
       "1999\t100\t100\t100\t100\n"
       "2000\t120\t120\t120\t120\n"
       "____ комментарий\n"
       "новый заголовок next table\n"
       "\t\tI\tII\tIII\tIV\n"
       "2001\t300\t300\t300\t300\n")
CSV = ['заголовок1 header1\t\t\t',
       'заголовок2 header2\t\t\t',
       '\t\tI\tII\tIII\tIV',
       '1999\t100\t100\t100\t100',
       '2000\t120\t120\t120\t120',
       '____ комментарий',
       'новый заголовок next table',
       '\t\tI\tII\tIII\tIV',
       '2001\t300\t300\t300\t300']

CSV_SPLIT = [{'datarow_strings': ['1999\t100\t100\t100\t100',
                                  '2000\t120\t120\t120\t120'],
              'header_strings': ['заголовок1 header1\t\t\t',
                                 'заголовок2 header2\t\t\t',
                                 '\t\tI\tII\tIII\tIV']},
             {'datarow_strings': ['2001\t300\t300\t300\t300'],
              'header_strings': ['____ комментарий',
                                 'новый заголовок next table',
                                 '\t\tI\tII\tIII\tIV']}]

TABLE_1 = Table(
    name=None,
    unit=None,
    row_format=None,
    header_strings=[
        'заголовок1 header1\t\t\t',
        'заголовок2 header2\t\t\t',
        '\t\tI\tII\tIII\tIV'],
    datarow_strings=[
        '1999\t100\t100\t100\t100',
        '2000\t120\t120\t120\t120'])

TABLE_2 = Table(
    name=None,
    unit=None,
    row_format=None,
    header_strings=[
        'новый заголовок next table',
        '\t\tI\tII\tIII\tIV'],
    datarow_strings=['2001\t300\t300\t300\t300'])


def test_get_tables_on_file():
    with TempFile(content=DOC) as filename:
        assert read_tables(filename) == [TABLE_1, TABLE_2]


def test_split_csv():
    assert split_csv(CSV) == CSV_SPLIT


def test_Table_headers_property():
    assert TABLE_1.headers == [
        'заголовок1 header1\t\t\t',
        'заголовок2 header2\t\t\t',
        '\t\tI\tII\tIII\tIV']


def test_Table_repr_is_callable():
    assert repr(TABLE_1)
    assert repr(TABLE_2)


def test_read_csv_from_string():
    with TempFile(DOC) as f:
        rows = list(read_csv(f))
        assert rows == CSV

# FIXME: add Table class tests
