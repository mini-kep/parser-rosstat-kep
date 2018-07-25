import kep.commands as commands
import pytest


def extract_command_parameters(command):
    if isinstance(command, str):
        method = command
        arg = None
    elif isinstance(command, dict):
        for method, arg in command.items():
            break
    else:
        raise TypeError(command)
    return method, arg


@pytest.mark.parametrize('command, tup', [
     ['init', ('init', None)],
     [{'set_name': 'INDPRO'}, ('set_name', 'INDPRO')]
])
def test_extract_command_parameters(command, tup):
    assert extract_command_parameters(command) == tup


def test_labels():
    res = commands.labels([{'set_name': 'INDPRO'}, {'set_units': 'yoy'}])
    assert res == ['INDPRO_yoy']    
    

def test_CommandSet_properties_are_callable():
    cs = commands.CommandSet([{'set_name': 'INDPRO'}, {'set_units': 'yoy'}])
    assert cs.methods
    assert cs.labels
