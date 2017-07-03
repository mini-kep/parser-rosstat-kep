# -*- coding: utf-8 -*-
"""
"""
import pytest

import itertools
from tempfile import NamedTemporaryFile
from pathlib import Path

import parse
import splitter

@pytest.fixture
def _pdef():
    from cfg import Definition
    # WONTFIX: name MAIN is rather useless for Definition instance
    pdef = Definition("MAIN")
    pdef.add_header("Объем ВВП", "GDP")
    # WONTFIX: not testing boundaries here
    pdef.add_marker(None, None)
    pdef.require("GDP", "bln_rub")
    pdef.add_header("Индекс промышленного производства", "IND_PROD")
    pdef.require("IND_PROD", "yoy")
    return pdef

@pytest.fixture
def _units():
    # IDEA: may use explicit hardcoded constant with less units
    from cfg import UNITS
    return UNITS

SAMPLE_HEADER = "\n".join([
    # junk below
    # skip empty rows
    "",    
    # skip comment
    "_____ Примечание",    
    # skip empty first cell
    "\t----this line will not be read ----",    
    # end junk
    # parse variable name 'GDP' from here
    "Объем ВВП" + "\t" * 4,
    # parse nothing from here, has "undefined lines" flag is raised
    "(уточненная оценка)",
    # parse unit 'bln_rub' form here
    "млрд.рублей" + "\t" * 4])    
SAMPLE_DATA = "\t".join(["1991 1)", "100", "20", "30", "40", "10"])
TABLE_TEXT = "\n".join([SAMPLE_HEADER, SAMPLE_DATA]) 

# FIXME: maybe use a more simple csv for second header
SAMPLE_HEADER_2 = "\n".join(['Индекс промышленного производства', 
                             'в % к соответствующему периоду предыдущего года'])
q_values = ['101,1', '102,2', '103,3', '104,3']
m_values = list(itertools.chain.from_iterable([x] * 3 for x in q_values))
SAMPLE_DATA_2 = "\t".join(['1991'] + ['102,7'] + q_values +  m_values)
# END FIXME -----------------

CSV_TEXT = "\n".join([TABLE_TEXT, SAMPLE_HEADER_2, SAMPLE_DATA_2])                      
                      
class MockCSV():
    def __init__(self, contents):
       with NamedTemporaryFile('w') as f:
            self.path = f.name
       Path(self.path).write_text(contents, encoding='utf-8')
    def close(self):
       Path(self.path).unlink()

@pytest.fixture
def csv_path():
    mock = MockCSV(CSV_TEXT) 
    yield Path(mock.path)
    mock.close()

def test_csv_path_fixture(csv_path):
    assert csv_path.exists()
    assert CSV_TEXT == csv_path.read_text(encoding='utf-8')

def test_read_csv(csv_path):    
    rows = parse.read_csv(csv_path)
    row_strings = ["Row <Объем ВВП>",
                   "Row <(уточненная оценка)>",
                   "Row <млрд.рублей>",
                   "Row <1991 1) | 100 20 30 40 10>",
                   "Row <Индекс промышленного производства>",
                   "Row <в % к соответствующему периоду предыдущего года>",
                   "Row <1991 | 102,7 101,1 102,2 103,3 104,3 101,1 101,1 101,1 102,2 102,2 102,2 103,3 103,3 103,3 104,3 104,3 104,3>"]
    for r, string in zip(rows, row_strings):
        assert r.__str__() == string


@pytest.fixture
def header_rows():
    mock = MockCSV(SAMPLE_HEADER) 
    header_path = Path(mock.path)
    yield parse.read_csv(header_path)
    mock.close()

class Test_Header_Rows:        
    def test_str_method_retruns_representation_string(self, header_rows):
        hrows = [r.__str__() for r in header_rows]
        assert hrows[0] == "Row <Объем ВВП>"
        assert hrows[1] == "Row <(уточненная оценка)>"
        assert hrows[2] == "Row <млрд.рублей>"   

@pytest.fixture
def header(header_rows):
    return parse.Header(header_rows)

class Test_Header:        
    
    def test_KNOWN_UNKNOWN_sanity(self):
        # actual error before class constants were introduced
        assert parse.Header.KNOWN != parse.Header.UNKNOWN
    
    # on creation
    
    def test_on_creation_varname_and_unit_is_none(self, header):
        assert header.varname is None
        assert header.varname is None
        
    def test_on_creation_textlines_is_list_of_strings(self, header):
        # IDEA: why to we still need .textlines? can access them from .processed
        header.textlines == ['Объем ВВП', 
                             '(уточненная оценка)', 
                             'млрд.рублей']

    def test_on_creation_processed_is_unknown(self, header):
        assert header.processed['Объем ВВП'] == parse.Header.UNKNOWN 
        assert header.processed['млрд.рублей'] == parse.Header.UNKNOWN 

    def test_on_creation_has_unknown_lines(self, header):
        assert header.has_unknown_lines() is True

    def test_on_creation_str(self, header):
        assert header.__str__() == 'varname: None, unit: None\n- <Объем ВВП>\n- <(уточненная оценка)>\n- <млрд.рублей>'

    # after parsing 
        
    def test_set_varname_results_in_GDP(self, header, _pdef, _units):
        header.set_varname(pdef=_pdef, units=_units)
        # IDEA: isolate work with units in set_varname() method 
        assert header.varname == 'GDP'        
        assert header.processed['Объем ВВП'] == parse.Header.KNOWN  
     
    def test_set_unit_results_in_bln_rub(self, header, _units):
        header.set_unit(units=_units)
        assert header.unit == 'bln_rub' 
        assert header.processed['млрд.рублей'] == parse.Header.KNOWN  

    def test_after_parsing_has_unknown_lines(self, header, _pdef, _units):
        header.set_unit(units=_units)
        header.set_varname(pdef=_pdef, units=_units)
        assert header.has_unknown_lines() is True

    def test_after_parsing_str(self, header):
        assert header.__str__() == ('varname: None, unit: None\n'
                                    '- <Объем ВВП>\n'
                                    '- <(уточненная оценка)>\n'
                                    '- <млрд.рублей>')

@pytest.fixture
def tables(csv_path, _pdef, _units):
    rows = parse.read_csv(csv_path)
    return parse.get_tables_from_rows_segment(rows, _pdef, _units)

@pytest.fixture
def table(tables):
    return tables[0]

class Test_Table_except_header():
    
    # FIXME: apparently cannot pass fixture to a setup_mathod in pytest
    #def setup_method(self):
    #    self.table = sample_table_gdp()

    def test_Table_instance_column_number(self, table):
        assert table.coln == 5

    def test_Table_instance_datarows(self, table):
        assert len(table.datarows) == 1
        row = table.datarows[0]
        assert row.name == '1991 1)'
        assert row.data == ["100", "20", "30", "40", "10"]        
        
    def test_Table_instance_has_splitter(self, table):     
        assert table.splitter_func == splitter.split_row_by_year_and_qtr
                
    def test_Table_is_defined(self, table):
        assert table.is_defined() is True

    def test_Table_label(self, table):
        assert table.label == 'GDP_bln_rub'

    def test_Table_repr(self, table):
        assert table.__repr__() == 'Table GDP_bln_rub (headers: 3, datarows: 1)'

    def test_Table_str(self, table):
        print(table)
        assert table.__str__() == """Table GDP_bln_rub
columns: 5
varname: GDP, unit: bln_rub
+ <Объем ВВП>
- <(уточненная оценка)>
+ <млрд.рублей>
Row <1991 1) | 100 20 30 40 10>"""
            

@pytest.fixture
def emitter(tables):    
    return parse.Emitter(tables[0])

@pytest.fixture
def datapoints(tables):    
    return parse.Datapoints(tables)

@pytest.fixture
def frames(datapoints):
    return parse.Frames(datapoints)
            
def test_emitter(emitter):
    e = emitter
    assert e.emit_a() == [{'freq': 'a', 'label': 'GDP_bln_rub', 'value': 100.0, 'year': 1991}]
    assert {'freq': 'q', 'label': 'GDP_bln_rub', 'qtr': 1, 'value': 20.0,
            'year': 1991} in e.emit_q()
    assert [] == e.emit_m()

def test_datapoints(datapoints):
    pts = datapoints    
    # gdp
    assert pts.is_included({'year': 1991, 'label': 'GDP_bln_rub', 'freq': 'a', 'value': 100.0})
    assert pts.is_included({'year': 1991, 'label': 'GDP_bln_rub', 'freq': 'q', 'value': 40.0, 'qtr': 3})    
    # ind_prod    
    assert pts.is_included({'year': 1991, 'label': 'IND_PROD_yoy', 'freq': 'a', 'value': 102.7})    
    assert pts.is_included({'year': 1991, 'label': 'IND_PROD_yoy', 'freq': 'q', 'value': 102.2, 'qtr': 2})
    assert pts.is_included({'year': 1991, 'label': 'IND_PROD_yoy', 'freq': 'm', 'value': 104.3, 'month': 12})

def test_frames(frames):
    f = frames
    assert f.dfa['GDP_bln_rub'].sum() == f.dfq['GDP_bln_rub'].sum()
    assert f.dfa['GDP_bln_rub'].sum() == 100
    # FIXME: add IND_yoy                        

if __name__ == "__main__":
    pytest.main(["test_header.py"])      