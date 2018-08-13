from kep.util.tempfile import TempFile

from kep.parameters import (load_yaml_list, load_yaml_one_document,
                            ParsingParameters, CheckParameters)


TEXT_1 = '- 123\n---\n- 456'
VALUE_1 = [[123], [456]]

TEXT_2 = '- abc\n- def'
VALUE_2 = [['abc', 'def']]


def test_load_yaml_list():
    with TempFile(TEXT_1) as f :
        load_yaml_list(f) == VALUE_1
        
def test_load_yaml_one_document():
    with TempFile(TEXT_2) as f :
        load_yaml_one_document(f) == VALUE_2

def test_ParsingParameters():
    p = ParsingParameters
    assert p.common_dicts
    assert p.segment_dicts
    assert p.units_dict  
    
    

def test_CheckParameters():
    c = CheckParameters
    assert c.group_dict
    assert c.mandatory_list
    assert c.optional_lists
