# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict as odict


from csv2df.specification import (UNITS, UNIT_NAMES, as_list, ParsingCommand,
                                  Def, Scope)


def test_UNITS():
    assert isinstance(UNITS, dict)


def test_UNIT_NAMES():
    assert set(UNIT_NAMES.keys()) == set(UNITS.values())


class Test_as_list():
    def test_single_arg(self):
        assert as_list("a") == ["a"]
        assert as_list(["a"]) == ["a"]
        assert as_list(1) == [1]

    def test_list_arg(self):
        assert as_list(["a", "b"]) == ["a", "b"]

    def test_tuple(self):
        tup = tuple(["a", "b"])
        assert as_list(tup) == ["a", "b"]


class Test_Scope:
    sc = Scope("Header 1", "Header 2")
    ah = "A bit rotten Header 1", "Curved Header 2."
    sc.add_bounds(*ah)
    good_rows = [ah[0],
                 'more lines here',
                 'more lines here',
                 'more lines here',
                 ah[1]]
    bad_rows = ['zzz' + ah[0],
                'more lines here',
                'more lines here',
                'more lines here',
                'zzz' + ah[1]]

    def test_repr(self):
        assert repr(self.sc)

    def test_able_to_find_bounds(self):
        s, e = self.sc.get_bounds(self.good_rows)
        assert s, e == self.ah

    def test_not_able_to_find_bounds(self):
        with pytest.raises(ValueError):
            _, _ = self.sc.get_bounds(self.bad_rows)


class Test_ParsingCommmand:
    pc = ParsingCommand(
        "GDP",
        headers=["Oбъем ВВП",
                 "Индекс физического объема произведенного ВВП, в %",
                 "Валовой внутренний продукт"],
        required_units=["bln_rub", "yoy"])

    def test_mapper_property_on_init_is_expected_dict(self):
        assert self.pc.mapper == \
            {'Oбъем ВВП': 'GDP',
                'Валовой внутренний продукт': 'GDP',
                'Индекс физического объема произведенного ВВП, в %': 'GDP'}

    def test_required_property_on_init_is_expected_list_of_strings(self):
        assert self.pc.required == ['GDP_bln_rub', 'GDP_yoy']

    def test_units_property_is_expected_list_of_strings(self):
        assert self.pc.units == ['bln_rub', 'yoy']


class Test_Parsing_Definition:
    _pc1 = ParsingCommand(
        "GDP",
        headers=[
            "Oбъем ВВП",
            "Индекс физического объема произведенного ВВП, в %",
            "Валовой внутренний продукт"],
        required_units=[
            "bln_rub",
            "yoy"])
    _pc2 = ParsingCommand("INDPRO",
                          headers="Индекс промышленного производства",
                          required_units=["yoy", "rog"])
    _sc = Scope("Header 1", "Header 2")
    pd = Def(commands=[_pc1, _pc2], scope=_sc, func_name='fiscal')

    def test_mapper_property(self):
        assert self.pd.mapper == \
            {'Oбъем ВВП': 'GDP',
             'Валовой внутренний продукт': 'GDP',
             'Индекс промышленного производства': 'INDPRO',
             'Индекс физического объема произведенного ВВП, в %': 'GDP'}

# FIXME:
#    def test_cannot_add_undefined_unit(self):
#        p = self.p
#        with pytest.raises(ValueError):
#            p.append("NEWVAR", text=str(),
#                     required_units="this_unit_doesnot_exit")

    def test_required_property(self):
        assert self.pd.required == [
            'GDP_bln_rub',
            'GDP_yoy',
            'INDPRO_yoy',
            'INDPRO_rog']

    def test_units_property(self):
        assert isinstance(self.pd.units, odict)

    def test_reader_property(self):
        # not defined, but present
        assert callable(self.pd.reader)

    def test_get_bounds(self):
        assert callable(self.pd.get_bounds)


if __name__ == "__main__":
    pytest.main([__file__])
