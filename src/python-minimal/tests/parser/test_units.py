from kep.parser.units import UnitMapper
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


def test_Unit_mapper_evaluate_returns_longest_unit():    
    mapper2 = UnitMapper({
        'yoy': ['в % к соответствующему периоду предыдущего года'],
        'ytd': ['период с начала отчетного года в % к соответствующему '
                'периоду предыдущего года'] 
            })
    assert 'ytd' == mapper2.extract('some text contaning...'
                                    'период с начала отчетного года '
                                    'в % к соответствующему '
                                    'периоду предыдущего года')
    