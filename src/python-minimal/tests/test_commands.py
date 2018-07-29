import kep.commands as commands
import pytest


@pytest.mark.parametrize('command, tup', [
     ['init', ('init', None)],
     [{'var': 'INDPRO'}, ('var', 'INDPRO')]
])
def test_extract_command_parameters(command, tup):
    assert commands._extract_command_parameters(command) == tup


def test_labels():
    res = commands._labels([{'var': 'INDPRO'}, {'units': 'yoy'}])
    assert res == ['INDPRO_yoy']    
    

def test_CommandSet_properties_are_callable():
    cs = commands.CommandSet([{'var': 'INDPRO'}, {'units': 'yoy'}])
    assert cs.methods
    assert cs.labels
    
# TODO: more tests for commands    
