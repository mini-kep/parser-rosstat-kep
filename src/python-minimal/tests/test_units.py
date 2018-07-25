from kep.units import UnitMapper
import pytest


mapper = UnitMapper({
        'bln_rub': ['млрд.рублей'], 
        'yoy': ['в % к соответствующему периоду предыдущего года']
        })

@pytest.mark.parametrize('unit, text', [
    ['bln_rub', 'abc - млрд.рублей'],
    ['yoy', 'в % к соответствующему периоду предыдущего года '
            '/ percent of corresponding period of previous year']
])

def test_Unit_mapper_evaluate_method(unit, text):
    assert unit == mapper.extract(text)
