from .shared import TempFile
from kep.reader import import_tables, read_csv, Table, split_to_tables

DOC = "header1\t\t\t\nheader2\t\t\t\n1999\t100\t100\t100\t100\n2000\t120\t120\t120\t120"
CSV = [['header1', '', '', ''],
       ['header2', '', '', ''],
       ['1999', '100', '100', '100', '100'],
       ['2000', '120', '120', '120', '120']]
TABLE = Table(name=None,
              unit=None,
              row_format=None,
              headrows=[['header1', '', '', ''], 
                           ['header2', '', '', '']],
              datarows=[['1999', '100', '100', '100', '100'],
                         ['2000', '120', '120', '120', '120']])

def test_Table_headers_property():
    assert TABLE.headers == ['header1', 'header2']

def test_split_to_tables():
    assert next(split_to_tables(CSV)) == TABLE

def test_read_csv_from_string():
    assert list(read_csv(DOC)) == CSV

def test_import_tables_from_string_on_one_table():
    tables = import_tables(DOC)
    assert tables[0] == TABLE
    
def test_import_tables_on_file():    
    with TempFile(content=DOC) as filename:
        tables = import_tables(filename)  
        assert tables[0] == TABLE
        
    