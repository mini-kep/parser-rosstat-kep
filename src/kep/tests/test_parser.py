import itertools
import pytest

# fixtures
from kep.reader import Row
# testing
from kep.parcer import Table, split_to_tables, extract_tables
from kep.specification import (ParsingInstruction, Definition, 
                               Specification)

# TODO: rename module 'rows'

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

# FIXME: Scope not tested


gdp_def = dict(varname="GDP",
               text='Объем ВВП',
               required_units=['bln_rub', 'rog'])

indpro_def = dict(varname="INDPRO",
                  text='Индекс промышленного производства',
                  required_units='yoy')


class Spec_Sample:

    def units():
        return {'млрд.рублей': 'bln_rub',
                'в % к прошлому периоду': 'rog',
                'в % к соответствующему периоду предыдущего года': 'yoy'}

    def indicator(name):
        inds = dict(GDP=ParsingInstruction(**gdp_def),
                    INDPRO=ParsingInstruction(**indpro_def))
        return inds[name]

    def pdef():
        pdef = Definition(reader=None)
        pdef.append(**gdp_def)
        pdef.append(**indpro_def)
        return pdef

    def spec():
        main = Definition()
        main.append(**gdp_def)
        main.append(**indpro_def)
        return Specification(main)

labels = {0:'GDP_bln_rub',
          1:'GDP_rog',
          2:'INDPRO_yoy'}

parsed_varnames = {0:'GDP',
            1:'GDP',
            2:'INDPRO'}

parsed_units = {0:'bln_rub',
                1:'rog',
                2:'yoy'}

headers = {0: [Row(['Объем ВВП', '', '', '', '']),
               Row(['млрд.рублей', '', '', '', ''])],
           1: [Row(['Индекс ВВП, в % к прошлому периоду/ GDP index, percent'])],
           2: [Row(['Индекс промышленного производства']),
               Row(['в % к соответствующему периоду предыдущего года'])]
           }

data_items = {0: [Row(["1991", "4823", "901", "1102", "1373", "1447"])],
              1: [Row(['1999', '106,4', '98,1', '103,1', '111,4', '112,0'])],
              2: [Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]
              }


class Sample(Spec_Sample):
    """Fixtures for testing"""
    def rows(i):
        return headers[i] + data_items[i]

    def headers(i):
        return headers[i]

    def data_items(i):
        return data_items[i]

    def table(i):
        return Table(headers[i], data_items[i])
    
    def table_parsed(i):
        t = Table(headers[i], data_items[i])
        t.varname = parsed_varnames[i]
        t.unit = parsed_units[i]        
        t.set_splitter(funcname=None)
        return t

    def label(i):
        return labels[i]


@pytest.fixture
def mock_rows():
    gen = iter(Sample.rows(i) for i in [0, 1, 2])
    return itertools.chain.from_iterable(gen)


class Test_fixtures:

    def test_mock_rows(self):
        assert list(mock_rows()) == [Row(['Объем ВВП', '', '', '', '']),
                                     Row(['млрд.рублей', '', '', '', '']),
                                     Row(['1991', '4823', '901', '1102', '1373', '1447']),
                                     Row(['Индекс ВВП, в % к прошлому периоду/ GDP index, percent']),
                                     Row(['1999', '106,4', '98,1', '103,1', '111,4', '112,0']),
                                     Row(['Индекс промышленного производства']),
                                     Row(['в % к соответствующему периоду предыдущего года']),
                                     Row(['1991', '102,7', '101,1', '102,2', '103,3', '104,4'])]

    def test_regression_same_string_used_in_first_row_and_pdef(self):
        assert [k for k in Sample.pdef().instr.varname_mapper][0] == \
            next(mock_rows()).name


class Test_split_to_tables():

    def test_split_to_tables(self, mock_rows):
        tables = list(split_to_tables(mock_rows))
        assert len(tables) == 3
        assert tables[0] == Sample.table(0)
        assert tables[1] == Sample.table(1)
        assert tables[2] == Sample.table(2)


class Test_Table_on_creation:

    def setup_method(self):
        self.table = Sample.table(0)

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
        self.table.headers = Sample.headers(0)
        self.table.datarows = Sample.data_items(0)

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
        t = Sample.table(0)
        t.set_label(varnames_dict={'Объем ВВП': 'GDP'},
                    units_dict={'млрд.рублей': 'bln_rub'})
        t.set_splitter(funcname=None)
        self.table_after_parsing = t

    def test_set_label(self):
        table = Sample.table(0)
        table.set_label({'Объем ВВП': 'GDP'}, {'млрд.рублей': 'bln_rub'})
        assert table.varname == 'GDP'
        assert table.lines['Объем ВВП'] == table.KNOWN
        assert table.unit == 'bln_rub'
        assert table.lines['млрд.рублей'] == table.KNOWN

    def test_set_splitter(self):
        table = Sample.table(0)
        table.set_splitter(None)
        from kep.util_row_splitter import split_row_by_year_and_qtr
        assert table.splitter_func == split_row_by_year_and_qtr

    def test_has_unknown_lines(self):
        assert self.table_after_parsing.has_unknown_lines() is False

    def test_str_and_repr(self):
        assert str(self.table_after_parsing)
        assert repr(self.table_after_parsing)


class Test_extract_tables_function:

    tables = extract_tables(csv_segment=mock_rows(), pdef=Sample.pdef())

    # FIXME:  more functions in extract_tables other than split tables

    def test_returns_list(self):
        assert isinstance(self.tables, list)

    def test_table0_is_table_instance(self):
        t0 = self.tables[0]
        assert isinstance(t0, Table)
        assert t0 == Sample.table(0)

    def test_table0_can_be_parsed_with_label_GDP_bln_rub(self):
        t0 = self.tables[0]
        t0.set_label(varnames_dict={'Объем ВВП': 'GDP'},
                     units_dict={'млрд.рублей': 'bln_rub'})
        assert t0.label == 'GDP_bln_rub'


# FIXME:
#    def test_yield_tables(self, ts=Sample.tables()):
#        gen = ts.yield_tables()
#        for i, t in enumerate(gen):
#            assert t == Sample.table(i)
#            assert t.label == Sample.label(i)


if __name__ == "__main__":
    pytest.main([__file__])
