# -*- coding: utf-8 -*-
"""
"""
import pytest
from tempfile import NamedTemporaryFile
from pathlib import Path
import parse

SAMPLE_HEADER_TEXT = "\n".join([
    # parse variable name 'GDP' from here
    "Объем ВВП" + "\t" * 4,
    # parse nothing from here, has undefined lines flag is raised
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
def header_csv_path():
    mock = MockCSV(SAMPLE_HEADER_TEXT) 
    yield mock.path
    mock.close()

def test_csv_header_fixture(header_csv_path):    
    assert Path(header_csv_path).exists()
    assert SAMPLE_HEADER_TEXT == Path(header_csv_path).read_text(encoding='utf-8')

@pytest.fixture
def header_rows(header_csv_path):
    path = Path(header_csv_path)
    return parse.read_csv(path)

class Test_Header_Rows:        
    def test_str_method_retruns_string(self, header_rows):
        hrows = [r.__str__() for r in header_rows]
        assert hrows[0] == "Row <Объем ВВП>"
        assert hrows[1] == "Row <(уточненная оценка)>"
        assert hrows[2] == "Row <млрд.рублей>"   



@pytest.fixture
def header_instance(header_rows):
    return parse.Header(header_rows)

#@pytest.fixture
#def sample_pdef():
#    from cfg import Definition
#    # WONTFIX: name MAIN is rather useless for Definition instance
#    pdef = Definition("MAIN")
#    pdef.add_header("Объем ВВП", "GDP")
#    pdef.add_marker(None, None)
#    pdef.require("GDP", "bln_rub")
#    pdef.add_header("Индекс промышленного производства", "IND_PROD")
#    pdef.require("IND_PROD", "yoy")
#    return pdef
#
#def units():
#    from cfg import UNITS
#    return UNITS
#
#
#class Test_Header:        
#    def setup_method(self):
#        self.raw_header = next(header_sample())
#    
#    def test_text_lines_property_is_list_of_strings(self):
#        assert self.raw_header.textlines == ['Объем ВВП', 
#                                             '(уточненная оценка)', 
#                                             'млрд.рублей']
#    def test_set_unit_results_in_bln_rub(self):
#        header = self.raw_header
#        header.set_unit(units=units())
#        header.unit == 'bln_rub'        
#
#    def test_set_varname_results_in_GDP(self):
#        header = self.raw_header
#        header.set_varname(pdef=sample_pdef(), units=units())
#        header.varname == 'GDP'        

if __name__ == "__main__":
    pytest.main(["test_header.py"])      