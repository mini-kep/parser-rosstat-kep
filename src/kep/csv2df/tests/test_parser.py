import pytest
import pandas as pd

from kep.csv2df.parser import Table, DataBlock, HeaderParser
from kep.csv2df.parser import timestamp_quarter, timestamp_month, timestamp_annual

from kep.csv2df.util.row_splitter import split_row_by_year_and_qtr
from kep.parsing_definition.units import UNITS
#TODO: rename globally
from kep.parsing_definition.parsing_definition import make_entry


@pytest.fixture
def table():
    headers = [['Объем ВВП', '', '', '', ''],
               ['млрд.рублей', '', '', '', '']]
    datarows = [['1991', '4823', '901', '1102', '1373', '1447']]    
    return Table(headers, datarows) 

@pytest.fixture
def parsed_table():
    t = table()  
    t.set_label(varnames_dict = {'Объем ВВП': 'GDP'},
                units_dict = {'млрд.рублей': 'bln_rub'})
    t.set_splitter(None)    
    return t

class Test_Table:

    def test_on_creation_pasring_attributes_are_unknown(self, table):
        assert table.label is None 
        assert table.splitter_func is None
        assert table.varname is None
        assert table.unit is None
        assert table.header.is_parsed is False        
        
    def test_on_creation_has_unknown_lines(self, table):
        assert table.has_unknown_lines() is True

    def test_str_repr(self, table):
        assert str(table)
        assert repr(table)    
        
    def test_set_label(self, table):        
        table.set_label(varnames_dict = {'Объем ВВП': 'GDP'},
                        units_dict = {'млрд.рублей': 'bln_rub'})
        assert table.varname == 'GDP'
        assert table.unit == 'bln_rub'
        assert table.label == 'GDP_bln_rub'
        assert table.has_unknown_lines() is False
        
    def test_set_splitter(self, table):
        table.set_splitter(None)
        assert table.splitter_func == split_row_by_year_and_qtr    
        
    def test_values_property_on_parsed_table(self, parsed_table):
        values = parsed_table.values
        assert len(values) == 5
        assert values[0] == {'label': 'GDP_bln_rub', 
                            'value': 4823.0, 
                            'time_index': pd.Timestamp('1991-12-31'), 
                            'freq': 'a'}
        assert values[-1] ==  {'label': 'GDP_bln_rub', 
                               'value': 1447.0, 
                               'time_index': pd.Timestamp('1991-12-31'), 
                               'freq': 'q'}

def mock_rows():
    return [['Объем ВВП', '', '', '', ''],
               ['млрд.рублей', '', '', '', ''],
               ['1999', '4823', '901', '1102', '1373', '1447'],
               ['Индекс ВВП, в % к прошлому периоду/ GDP index, percent'],
               ['1999', '106,4', '98,1', '103,1', '111,4', '112,0'],
               ['Индекс промышленного производства'],
               ['в % к соответствующему периоду предыдущего года'],
               ['1999', '102,7', '101,1', '102,2', '103,3', '104,4']]


def parsing_definition():
    gdp_def = dict(var="GDP",
                   header='Объем ВВП',
                   unit=['bln_rub', 'rog'])
    indpro_def = dict(var="INDPRO",
                      header='Индекс промышленного производства',
                      unit='yoy')
    return Definition(commands=[gdp_def, indpro_def], units=UNITS)

# FIXME: is this for deleting?
# def test_extract_tables():
    # seg = Segment(mock_rows(), parsing_definition())
    # tables = seg.extract_tables()
    # assert isinstance(tables, list)
    # assert len(tables) == 3 
    # assert isinstance(tables[0], Table)
    
    
class Test_HeaderParser:
    def setup(self):
        self.progress = HeaderParser([['abc', 'zzz'], ['def', 'yyy']])

    def test_on_init_is_parsed_returns_false(self):
        assert self.progress.is_parsed is False
         
    def test_set_label(self):
        a, b = self.progress.set_label({'abc': 1}, {'def':2})
        assert a == 1
        assert b == 2
        assert self.progress.is_parsed is True
        
    def test_str(self):
        assert str(self.progress)    

class Test_DataBlock:    
    def test_extract_values_on_complete_row_returns_5_dictionaries(self):
        datablock = DataBlock(datarows=[['1999', '4823', '901', 
                                     '1102', '1373', '1447']],
                              label='GDP_bln_rub',
                              splitter_func = split_row_by_year_and_qtr)        
        values = list(datablock.extract_values())
        assert len(values) == 5

    def test_extract_values_on_incomplete_row_returns_less_dictionaries(self):
        datablock = DataBlock(datarows=[['1999', '', '901', 
                                     '1102', '', '']],
                              label='GDP_bln_rub',
                              splitter_func = split_row_by_year_and_qtr) 
        values = list(datablock.extract_values())
        assert len(values) == 2


def test_timestamp_quarter():
    assert timestamp_quarter(1999, 1) == pd.Timestamp('1999-03-31')


def test_timestamp_month():
    assert timestamp_month(1999, 1) == pd.Timestamp('1999-01-31')


def test_timestamp_annual():
    assert timestamp_annual(1999) == pd.Timestamp('1999-12-31')
    

if __name__ == "__main__":
    pytest.main([__file__])
    

    
