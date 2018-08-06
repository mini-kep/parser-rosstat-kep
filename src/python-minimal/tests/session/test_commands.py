from kep.session.commands import extract_parameters, extract_labels


def test_extract_command_parameters():
    assert extract_parameters({'var': 'INDPRO'}, ['var']) == ('var', 'INDPRO')
    assert extract_parameters('init', ['init']) == ('init', None)


def test_labels():
    res = extract_labels([('var', 'INDPRO'), ('units', 'yoy')])
    assert res == ['INDPRO_yoy']    
    

