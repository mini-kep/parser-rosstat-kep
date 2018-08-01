import pytest
from .shared import TempFile

from kep.interface import load_yaml 

    
TEXT_1 = '- 123\n---\n- 456'
VALUE_1 = [[123], [456]]

TEXT_2 = '- abc\n- def'
VALUE_2 = ['abc', 'def']

    
class Test_load_yaml():

    def test_on_strings(self):
        assert load_yaml(TEXT_1) == VALUE_1
        assert load_yaml(TEXT_2) == VALUE_2
        
        
    def test_on_filenames(self):
        for a, b in [(TEXT_1, VALUE_1), (TEXT_2, VALUE_2)]:
            with TempFile(a) as filename:
                assert load_yaml(filename) == b        
        
    def test_on_int_raises_TypeError(self):   
        with pytest.raises(TypeError):
            load_yaml(1)
    