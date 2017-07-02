# -*- coding: utf-8 -*-
"""
"""
import pytest
from tempfile import NamedTemporaryFile
from pathlib import Path
import parse

SAMPLE_HEADER = "\n".join([
    # skip empty rows
    "",    
    # parse variable name 'GDP' from here
    "Объем ВВП" + "\t" * 4,
    # parse nothing from here, has "undefined lines" flag is raised
    "(уточненная оценка)",
    # parse unit 'bln_rub' form here
    "млрд.рублей" + "\t" * 4])

class MockCSV():
    def __init__(self, contents):
       with NamedTemporaryFile('w') as f:
            self.path = f.name
       Path(self.path).write_text(contents, encoding='utf-8')
    def close(self):
       Path(self.path).unlink()
        
@pytest.fixture
def header_path():
    mock = MockCSV(SAMPLE_HEADER) 
    yield Path(mock.path)
    mock.close()

def test_csv_header_fixture(header_path):
    assert header_path.exists()
    assert SAMPLE_HEADER == header_path.read_text(encoding='utf-8')

@pytest.fixture
def header_rows(header_path):
    return parse.read_csv(header_path)

class Test_Header_Rows:        
    def test_str_method_retruns_representation_string(self, header_rows):
        hrows = [r.__str__() for r in header_rows]
        assert hrows[0] == "Row <Объем ВВП>"
        assert hrows[1] == "Row <(уточненная оценка)>"
        assert hrows[2] == "Row <млрд.рублей>"   

@pytest.fixture
def header(header_rows):
    return parse.Header(header_rows)

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
    # IDEA: may use explicit hardcoded constant
    from cfg import UNITS
    return UNITS

class Test_Header:        
    
    def test_textlines_property_is_list_of_strings(self, header):
        header.textlines == ['Объем ВВП', 
                             '(уточненная оценка)', 
                             'млрд.рублей']
        
    def test_set_unit_results_in_bln_rub(self, header, _units):
        header.set_unit(units=_units)
        assert header.unit == 'bln_rub'        

    def test_set_varname_results_in_GDP(self, header, _pdef, _units):
        header.set_varname(pdef=_pdef, units=_units)
        # IDEA: isolate work with units in set_varname() method 
        assert header.varname == 'GDP'        

    def test_has_unknown_lines(self, header, _pdef, _units):
        header.set_unit(units=_units)
        header.set_varname(pdef=_pdef, units=_units)
        assert header.has_unknown_lines() is True

if __name__ == "__main__":
    pytest.main(["test_header.py"])      