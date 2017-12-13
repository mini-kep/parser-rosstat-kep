# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict as odict

from definitions.units import UNITS
from csv2df.specification import as_list, ParsingCommand, Def, Scope


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
    boundaries = [dict(start="Header 1", end="Header 2"),
                  dict(start="A bit rotten Header 1", 
                         end="Curved Header 2.")]
    sc = Scope(boundaries)
    good_rows = ['Header 1',
                 'more lines here',
                 'more lines here',
                 'more lines here',
                 'Header 2']
    bad_rows = ['zzz',
                'more lines here',
                'more lines here',
                'more lines here',
                'yyy']

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
        header=["Oбъем ВВП",
                 "Индекс физического объема произведенного ВВП, в %",
                 "Валовой внутренний продукт"],
        unit=["bln_rub", "yoy"])

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
    commands = [dict(
        var='GDP',
        header=[
            "Oбъем ВВП",
            "Индекс физического объема произведенного ВВП, в %",
            "Валовой внутренний продукт"],
        unit=[
            "bln_rub",
            "yoy"]), 
                dict(    
         var="INDPRO",
         header="Индекс промышленного производства",
         unit=["yoy", "rog"])]
    boundaries = dict(start="Header 1", end="Header 2")
    pd = Def(commands, boundaries, reader='fiscal')

    def test_mapper_property(self):
        assert self.pd.mapper == \
            {'Oбъем ВВП': 'GDP',
             'Валовой внутренний продукт': 'GDP',
             'Индекс промышленного производства': 'INDPRO',
             'Индекс физического объема произведенного ВВП, в %': 'GDP'}

    def test_required_property(self):
        assert self.pd.required == [
            'GDP_bln_rub',
            'GDP_yoy',
            'INDPRO_yoy',
            'INDPRO_rog']

    def test_units_property(self):
        assert isinstance(self.pd.units, odict)

    def test_reader_property(self):        
        assert isinstance(self.pd.reader, str)

    def test_get_bounds(self):
        assert callable(self.pd.get_bounds)


if __name__ == "__main__":
    pytest.main([__file__])
