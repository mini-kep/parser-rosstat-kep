import kep.commands as commands


def test_extract_command_parameters():
    assert commands.extract_parameters({'var': 'INDPRO'}) == ('var', 'INDPRO')
    assert commands.extract_parameters('init') == ('init', None)


def test_labels():
    res = commands.extract_labels([{'var': 'INDPRO'}, {'units': 'yoy'}])
    assert res == ['INDPRO_yoy']    
    

