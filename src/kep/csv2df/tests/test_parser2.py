import pytest
import pandas as pd

from kep.csv2df.parser import Table
from kep.csv2df.util.row_splitter import split_row_by_year_and_qtr


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
        assert table.datablock.splitter_func is None
        assert table.header.is_parsed() is False        
        
    def test_on_creation_has_unknown_lines(self):
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
        assert table.datablock.splitter_func == split_row_by_year_and_qtr    
        
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

if __name__ == "__main__":
    pytest.main([__file__])
    
t = parsed_table()
print(t.values)
    
