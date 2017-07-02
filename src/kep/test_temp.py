# -*- coding: utf-8 -*-
"""
"""
import pytest
from tempfile import NamedTemporaryFile
from pathlib import Path
import parse

header_csv_sample = "\n".join([
    # parse variable name 'GDP' from here
    "Объем ВВП" + "\t" * 4,
    # parse nothing from here, has undefined lines flag is raised
    "(уточненная оценка)",
    # parse unit 'bln_rub' form here
    "млрд.рублей" + "\t" * 4])

def make_tempfile(contents):
    with NamedTemporaryFile('w') as f:
        filename = f.name
    path = Path(filename)
    path.write_text(contents, encoding='utf-8')
    return path

@pytest.yield_fixture
def csv_path(text=""):
    filename = make_tempfile(text)
    yield filename
    Path(filename).unlink()

def test_selftest_csv_path_file_does_not_exist_when_fully_iterated():
    gen = csv_path(header_csv_sample)
    path = next(gen)
    assert header_csv_sample == Path(path).read_text(encoding='utf-8')
    try:
        next(gen)
    except StopIteration:
        assert not Path(path).exists()

@pytest.yield_fixture
def header_rows_sample():
    path = make_tempfile(header_csv_sample)
    yield parse.read_csv(path)
    Path(path).unlink()

@pytest.yield_fixture
def header_sample():
    path = make_tempfile(header_csv_sample)
    yield parse.Header(parse.read_csv(path))
    Path(path).unlink()

class Test_Header_Rows:        
    def test_str_method_retruns_string(self, header_rows_sample):
        hrows = [r.__str__() for r in header_rows_sample]
        assert hrows[0] == "Row <Объем ВВП>"
        assert hrows[1] == "Row <(уточненная оценка)>"
        assert hrows[2] == "Row <млрд.рублей>"   

class Test_Header:        
    def setup_method(self):
        self.header = next(header_sample())
    
    def test_text_lines_property_is_list_of_strings(self):
        assert self.header.textlines == ['Объем ВВП', '(уточненная оценка)', 
                                         'млрд.рублей']

if __name__ == "__main__":
    pytest.main(["test_temp.py"])      