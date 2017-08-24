import pytest
import kep.label as label

# TODO: add variable name with underscore, like GOV_EXPENSE


def test_make_label():
    assert label.make_label('GDP', 'bln_rub') == 'GDP_bln_rub'
    assert label.make_label('GDP', 'rog') == 'GDP_rog'
    assert label.make_label('PROD_E', 'TWh') == 'PROD_E_TWh'


def test_split_label():
    assert label.split_label('GDP_bln_rub') == ('GDP', 'bln_rub')
    assert label.split_label('GDP_rog') == ('GDP', 'rog')
    assert label.split_label('PROD_E_TWh') == ('PROD_E', 'TWh')
    # note the () for tuple above
    with pytest.raises(AssertionError):
        assert label.split_label('GDP_bln_rub') == 'GDP', 'bln_rub'


def test_extract_varname():
    assert label.extract_varname('GDP_bln_rub') == 'GDP'
    assert label.extract_varname('GDP_rog') == 'GDP'
    assert label.extract_varname('PROD_E_TWh') == 'PROD_E'


def test_extract_unit():
    assert label.extract_unit('GDP_bln_rub') == 'bln_rub'
    assert label.extract_unit('GDP_rog') == 'rog'
    assert label.extract_unit('PROD_E_TWh') == 'TWh'


if __name__ == "__main__":
    pytest.main([__file__])
