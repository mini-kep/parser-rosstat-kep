import pytest
from .shared import TempFile

import kep.util as util

def test_iterate():
    assert util.iterate('abc') == ['abc']



    
TEXT_1 = '- 123\n---\n- 456'
VALUE_1 = [[123], [456]]

TEXT_2 = '- abc\n- def'
VALUE_2 = [['abc', 'def']]

    
class Test_load_yaml():
    def test_on_strings(self):
        assert util.load_yaml(TEXT_1) == VALUE_1
        assert util.load_yaml(TEXT_2) == VALUE_2
        
        
    def test_on_filenames(self):
        for a, b in [(TEXT_1, VALUE_1), (TEXT_2, VALUE_2)]:
            with TempFile(a) as filename:
                assert util.load_yaml(filename) == b        
        
    def test_on_int_raises_TypeError(self):   
        with pytest.raises(TypeError):
            util.load_yaml(1)
    