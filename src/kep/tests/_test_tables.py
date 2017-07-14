import pytest
from kep.tables import Table, Tables, split_to_tables
from kep.rows import Row, RowStack

from kep.cfg import Definition, Specification


rows = [Row(['Индекс промышленного производства']),
        Row(['в % к соответствующему периоду предыдущего года']),
        Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]



@pytest.fixture
def spec():
    d = Definition("MAIN")
    d.add_header("Объем ВВП", "GDP")
    d.require("GDP", "bln_rub")
    _spec = Specification(d)
    
    d = Definition("IND_PROM")
    d.add_marker("Индекс промышленного производства", "End")
    d.add_header("Индекс промышленного производства", "IND_PROD")
    d.require("IND_PROD", "yoy")
    _spec.append(d)
    return _spec 

@pytest.fixture
def units():
    return {'млрд.рублей': 'bln_rub', 
            'в % к соответствующему периоду предыдущего года': 'yoy'}

def mock_row_stream():
    yield Row(['Объем ВВП', '', '',  '', ''])
    yield Row(['(уточненная оценка)'])
    yield Row(['млрд.рублей', '', '',  '', ''])
    yield Row(["1991", "4823", "901", "1102", "1373", "1447"])
    yield Row(['Индекс промышленного производства'])
    yield Row(['в % к соответствующему периоду предыдущего года'])
    yield Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])
    yield Row(['End', '', '',  '', ''])    


t0 = Table(headers=[Row(['Объем ВВП', '', '', '', '']), 
                    Row(['(уточненная оценка)']), 
                    Row(['млрд.рублей', '', '', '', ''])], 
          datarows=[Row(['1991', '4823', '901', '1102', '1373', '1447'])]
)

t1 = Table(headers=[Row(['Индекс промышленного производства']), 
                    Row(['в % к соответствующему периоду предыдущего года'])], 
          datarows=[Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]
)

class Test_split_to_tables():
    
    def setup_method(self):
        self.rows = list(mock_row_stream())
        
    def test_split_to_tables(self):
        tables = list(split_to_tables(self.rows))        
        assert len(tables) == 2
        assert tables[0] == t0 
        assert tables[1] == t1
    
def mock_RowStack():
    return RowStack(mock_row_stream())

@pytest.fixture
def mock_Tables():
   return Tables(mock_RowStack(), spec=spec(), units=units())

class Test_Tables:    
    
    def test_tables_property(self, mock_Tables):
        # tables appear in order of defintions parsing
        mock_Tables.tables[0] = t1
        mock_Tables.tables[1] = t0      
    
    def test_get_required(self, mock_Tables):
        tables = mock_Tables.get_required()
        # tables appear in order of defintions parsing
        tables[0] = t1
        tables[1] = t0      


#def to_row(d):
#    elements = [d['name']] + d['data']
#    return tables.Row(elements)
#
#
#@pytest.fixture
#def row_stack():
#    rows = [to_row(d) for d in ROWS]
#    return tables.RowStack(rows)
#
#
#class Test_RowStack():
#    def test_row_stack_fixture_self_test(self, row_stack):
#        for s, r in zip(row_stack.rows, ROWS):
#            assert s.name == r['name']
#            assert s.data == r['data']
#
#
#from cfg import Definition
#
#
#class Test_RowStack_stable_on_definition_with_None_markers:
#
#    def setup_method(self):
#        # pdef_with_two_None_markers
#        self.pdef1 = Definition("MAIN")
#        self.pdef1.add_marker(None, None)
#
#        # pdef_with_one_None_markers
#        self.pdef2 = Definition("MAIN")
#        self.pdef2.add_marker(None, "endline", must_check=False)
#
#    def test_pop_returns_segment(self, row_stack):
#        csv_segment = row_stack.pop(self.pdef1)
#        assert len(csv_segment) == 7
#
#    def test_pop_raises_ValueError_on_unsupported_def(self, row_stack):
#        with pytest.raises(ValueError):
#            row_stack.pop(self.pdef2)
#
#    def test_is_found_raises_error(self, row_stack):
#        with pytest.raises(AttributeError):
#            # error found in Rows
#            row_stack.is_found(None)
#
#
#@pytest.fixture
#def header():
#    return tables.Header(rows_for_header())
#
#
#@pytest.fixture
#def parsed_header():
#    pheader = header()
#    pheader.set_unit(units=_units())
#    pheader.set_varname(pdef=_pdef(), units=_units())
#    return pheader
#
#
#@pytest.fixture
#def _pdef():
#    from cfg import Definition
#    # WONTFIX: name MAIN is rather useless for Definition instance
#    pdef = Definition("MAIN")
#    pdef.add_header("Объем ВВП", "GDP")
#    # WONTFIX: not testing boundaries here
#    pdef.add_marker(None, None)
#    pdef.require("GDP", "bln_rub")
#    pdef.add_header("Индекс промышленного производства", "IND_PROD")
#    pdef.require("IND_PROD", "yoy")
#    return pdef
#
#
#@pytest.fixture
#def _units():
#    # IDEA: may use explicit hardcoded constant with less units
#    from cfg import UNITS
#    return UNITS
#
#
# TODO: restore Test_Header
#class Test_Header:
#
#    def test_KNOWN_UNKNOWN_sanity(self):
#        # actual error before class constants were introduced
#        assert tables.Header.KNOWN != tables.Header.UNKNOWN
#
#    # on creation
#
#    def test_on_creation_varname_and_unit_is_none(self, header):
#        assert header.varname is None
#        assert header.unit is None
#
#    def test_on_creation_textlines_is_list_of_strings(self, header):
#        # IDEA: why to we still need .textlines? can access them from
#        # .processed
#        assert header.textlines == ['Объем ВВП',
#                                    '(уточненная оценка)',
#                                    'млрд.рублей']
#
#    def test_on_creation_processed_is_unknown(self, header):
#        assert header.processed['Объем ВВП'] == tables.Header.UNKNOWN
#        assert header.processed['млрд.рублей'] == tables.Header.UNKNOWN
#
#    def test_on_creation_has_unknown_lines(self, header):
#        assert header.has_unknown_lines() is True
#
#    def test_on_creation_str(self, header):
#        assert header.__str__() == ('varname: None, unit: None\n'
#                                    'headers:\n'
#                                    '- <Объем ВВП>\n'
#                                    '- <(уточненная оценка)>\n'
#                                    '- <млрд.рублей>')
#    # after parsing
#
#    def test_set_varname_results_in_GDP(self, header, _pdef, _units):
#        header.set_varname(pdef=_pdef, units=_units)
#        # IDEA: isolate work with units in set_varname() method
#        assert header.varname == 'GDP'
#        assert header.processed['Объем ВВП'] == tables.Header.KNOWN
#
#    def test_set_unit_results_in_bln_rub(self, header, _units):
#        header.set_unit(units=_units)
#        assert header.unit == 'bln_rub'
#        assert header.processed['млрд.рублей'] == tables.Header.KNOWN
#
#    def test_after_parsing_has_unknown_lines(self, parsed_header):
#        assert parsed_header.has_unknown_lines() is True
#
#    def test_after_parsing_str(self, parsed_header):
#        assert parsed_header.__str__() == ('varname: GDP, unit: bln_rub\n'
#                                           'headers:\n'
#                                           '+ <Объем ВВП>\n'
#                                           '- <(уточненная оценка)>\n'
#                                           '+ <млрд.рублей>')
#
#
if __name__ == "__main__":
    pytest.main([__file__])