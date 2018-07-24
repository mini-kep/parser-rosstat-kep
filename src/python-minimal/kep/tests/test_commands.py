from kep.commands import Commands

mapper = UnitMapper(BASE_UNITS)   

import pytest
@pytest.mark.parametrize('labels, doc', [
    [['ABC_xxx'], 
      '- set_name: ABC\n- set_units: xxx'],
    [['ABC_xxx', 'ABC_yyy'], 
      '- set_name: ABC\n- set_units: \n  - xxx\n  - yyy']
])
def test_command_labels(labels, doc):
    assert Commands(doc).labels() == labels
    
    