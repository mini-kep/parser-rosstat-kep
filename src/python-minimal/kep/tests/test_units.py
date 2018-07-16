from kep.units import UnitMapper, BASE_UNITS

mapper = UnitMapper(BASE_UNITS)   

import pytest
@pytest.mark.parametrize('unit, text', [
    ['bln_rub', 'abc - млрд.рублей'],
    ['yoy', 'в % к соответствующему периоду предыдущего года '
            '/ percent of corresponding period of previous year']
])

def test_Unit_mapper_evaluate_method(unit, text):
    assert unit == mapper.extract(text)