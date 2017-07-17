import itertools
import pytest

from kep.tables import Table, Tables, split_to_tables
from kep.rows import Row

# FIXME: test for label handling
#    def make_label(vn, unit, sep="_"):
#    return vn + sep + unit
#
#
# def split_label(label):
#    return extract_varname(label), extract_unit(label)
#
#
# def extract_varname(label):
#    words = label.split('_')
#    return '_'.join(itertools.takewhile(lambda word: word.isupper(), words))
#
#
# def extract_unit(label):
#    words = label.split('_')
#    return '_'.join(itertools.dropwhile(lambda word: word.isupper(), words))

# FIXME: csv to rows testing

header0 = [Row(['Объем ВВП', '', '', '', '']),
           Row(['млрд.рублей', '', '', '', ''])]
data0 = [Row(["1991", "4823", "901", "1102", "1373", "1447"])]


def yield_rows(headers, data):
    for h in headers:
        yield h
    for d in data:
        yield d
        
@pytest.fixture
def rows0():
    return yield_rows(header0, data0)    

@pytest.fixture
def table0():
    return Table(header0, data0)    

def rows1():
    yield Row(['Индекс ВВП, в % / GDP index, percent'])
    yield Row(['1999', '106,4', '98,1', '103,1', '111,4',  '112,0'])
   
def rows2():
    yield Row(['Индекс промышленного производства'])
    yield Row(['в % к соответствующему периоду предыдущего года'])
    yield Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])

@pytest.fixture
def mock_rows():
    return itertools.chain(rows0(), rows1(), rows2())

assert list(mock_rows()) == [Row(['Объем ВВП', '', '', '', '']),
 Row(['млрд.рублей', '', '', '', '']),
 Row(['1991', '4823', '901', '1102', '1373', '1447']),
 Row(['Индекс ВВП, в % / GDP index, percent']),
 Row(['1999', '106,4', '98,1', '103,1', '111,4', '112,0']),
 Row(['Индекс промышленного производства']),
 Row(['в % к соответствующему периоду предыдущего года']),
 Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]

#FIXME: table1

@pytest.fixture
def table2():
    return Table(headers=[Row(['Индекс промышленного производства']),
                          Row(['в % к соответствующему периоду предыдущего года'])],
                 datarows=[Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]
                 )

#TODO: rename moule rows
csvtext=dict()
headers={0:header0}
data={0:data0}
#def rowstream
table=dict()


class Sample:
    from kep.spec import Indicator
    Indicator = dict(GDP=Indicator(varname="GDP",
                     text='Объем ВВП',
                     required_units="bln_rub"))    


def units_sample():
    return {'млрд.рублей': 'bln_rub'} # add 2 units


def i_gdp():    
    return Sample.Indicator["GDP"]

# TODO: more to pdef spec


def pdef_sample():
    from kep.spec import Definition
    pdef = Definition()
    pdef.append(varname="GDP",
                text='Объем ВВП',
                required_units="bln_rub")
    return pdef


# test pdef fixture
assert [k for k in pdef_sample().headers][0] == next(mock_rows()).name


def spec_sample():
    from kep.spec import Definition, Specification
    main = Definition()
    main.append(varname="GDP",
                text='Объем ВВП',
                required_units="bln_rub")
    return Specification(main)


@pytest.fixture
def mock_Tables():
    return Tables(mock_rows(), spec=spec_sample(), units=units_sample())







class Test_split_to_tables():

    def test_split_to_tables(self, mock_rows):
        tables = list(split_to_tables(mock_rows))
        assert len(tables) == 3
        assert tables[0] == table0()
        # table 1
        assert tables[2] == table2()


class Test_Table_on_creation:

    def setup_method(self):
        self.table = table0()

    def test_KNOWN_UNKNOWN_sanity(self):
        # actual error before class constants were introduced
        assert self.table.KNOWN != self.table.UNKNOWN

    def test_on_creation_varname_and_unit_and_splitter_are_none(self):
        assert self.table.varname is None
        assert self.table.unit is None
        assert self.table.splitter_func is None

    def test_on_creation_coln(self):
        assert self.table.coln == 5

    def test_on_creation_header_and_datarows(self):
        self.table.headers = header0
        self.table.datarows = data0

    def test_on_creation_lines_is_unknown(self):
        assert self.table.lines['Объем ВВП'] == self.table.UNKNOWN
        assert self.table.lines['млрд.рублей'] == self.table.UNKNOWN

    def test_on_creation_has_unknown_lines(self):
        assert self.table.has_unknown_lines() is True

    def test_str_repr(self):
        assert str(self.table)
        assert repr(self.table)


class Test_Table_after_parsing:

    def setup_method(self):
        self.table_after_parsing = table0().parse(
            varnames_dict={
                'Объем ВВП': 'GDP'}, units_dict={
                'млрд.рублей': 'bln_rub'}, funcname=None)

    def test_set_label(self):
        table = table0()
        table.set_label({'Объем ВВП': 'GDP'}, {'млрд.рублей': 'bln_rub'})
        assert table.varname == 'GDP'
        assert table.lines['Объем ВВП'] == table.KNOWN
        assert table.unit == 'bln_rub'
        assert table.lines['млрд.рублей'] == table.KNOWN

    def test_set_splitter(self):
        table = table0()
        table.set_splitter(None)
        from kep.splitter import split_row_by_year_and_qtr
        assert table.splitter_func == split_row_by_year_and_qtr

    def test_has_unknown_lines(self):
        assert self.table_after_parsing.has_unknown_lines() is False

    def test_str_and_repr(self):
        assert str(self.table_after_parsing)
        assert repr(self.table_after_parsing)



def extract_sample():
    extract = mock_Tables().extract_tables
    return extract(csv_segment=list(rows0()),
                   pdef=pdef_sample(),
                   units_dict=units_sample())


class Test_Tables:

    def setup_method(self):
        self.ts = mock_Tables()

    def test_extract_tables_static_method(self):
        y = extract_sample()
        assert isinstance(y, list)
        t = y[0]
        assert isinstance(t, Table)
        assert t == table0()
        # FIXME: separate test
        t.parse(varnames_dict={'Объем ВВП': 'GDP'},
                units_dict={'млрд.рублей': 'bln_rub'},
                funcname=None)
        assert t.label == 'GDP_bln_rub'

    def test_spec_get_main_parsing_definition_returns_(self):
        pdef = self.ts.spec.get_main_parsing_definition()
        assert pdef == pdef_sample()

    def test_yield_tables(self):
        z = next(self.ts.yield_tables())
        assert z == table0()
        assert z.label == 'GDP_bln_rub'

     # TODO: write what is not tested


if __name__ == "__main__":
    pytest.main([__file__])
