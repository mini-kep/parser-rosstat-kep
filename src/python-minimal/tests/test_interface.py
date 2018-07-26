import kep.interface as interface

def test_str_to_yaml_many_works_on_one_document():
    assert interface._str_to_yaml_many("""- abc\n- def""") == [['abc', 'def']]