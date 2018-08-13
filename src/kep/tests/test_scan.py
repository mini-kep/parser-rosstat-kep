#def test_1():
#    parsing_parameters = get_parsing_parameters('instructions.yml')    
#    base_mapper = get_unit_mapper('base_units.yml') 
#    tables = get_tables(2009, 4)
#    t = find(tables, 'Ввод в действие жилых домов организациями всех форм собственности')
#    p = parsing_parameters[2]
#    parse_units([t], BASE_MAPPER)
#    parse_after_units([t], **p)
#    assert t.name == 'DWELL'
#    assert t.unit == 'mln_m2' 