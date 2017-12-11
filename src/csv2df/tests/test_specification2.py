# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict as odict

import csv2df.specification as spec

from csv2df.specification import as_list, ParsingInstruction
from csv2df.specification import Definition, Scope

from csv2df.specification import Specification


def test_UNITS():
    assert isinstance(spec.UNITS, dict)


def test_UNIT_NAMES():
    assert set(spec.UNIT_NAMES.keys()) == set(spec.UNITS.values())


class Test_as_list():
    def test_single_arg(self):
        assert as_list("a") == ["a"]
        assert as_list(["a"]) == ["a"]

    def test_list_arg(self):
        assert as_list(["a", "b"]) == ["a", "b"]

    def test_tuple(self):
        # NOTE: this is really a border case and there is some cost/benefit adding it to as_list function
        #
        #        +: it is good to think about "other options"
        #
        #        -: "other options" are endless, and we can rather raise
        #           error in bulk if we think that probability of bordercase
        #           appeareing if low. as_list operates on written instruction,
        #           so here we can assume one follows convention. appearance of
        #           tuple is a rare hapening.
        #
        #           In other words, it is a bit of 'made-up' situation and probably
        #           in this case not worth the effort. Also had to change to another elif
        #           to ensure the output is always a list.
        #
        #        I'm writing this because cost/benefit tradeoff becomes more
        #        important in rest of code, where some border cases are critical and some are not.
        #
        tup = tuple(["a", "b"])
        assert as_list(tup) == ["a", "b"]

    def test_argument_of_wrong_type(self):
        with pytest.raises(TypeError):
            as_list(1)


class Test_ParsingInstruction:

    # our fixture is instance with one append()
    p = ParsingInstruction()
    p.append(varname="GDP",
             text=["Oбъем ВВП",
                   "Индекс физического объема произведенного ВВП, в %"],
             required_units=["bln_rub", "yoy"],
             desc="Валовый внутренний продукт")

    def test_init(self):
        # dumb test class is callable
        # (will fail earlier, if not working)
        ParsingInstruction()

    def test_attribute_varname_mapper_after_signle_append(self):
        assert self.p.varname_mapper == odict(
            [('Oбъем ВВП', 'GDP'),
             ('Индекс физического объема произведенного ВВП, в %', 'GDP')])

    def test_attribute_descriptions_after_signle_append(self):
        assert self.p.descriptions == odict(
            {"GDP": "Валовый внутренний продукт"})

    def test_attribute_required_labels_after_signle_append(self):
        assert self.p.required_labels == ['GDP_bln_rub', 'GDP_yoy']

    def test_can_add_variable_only_once(self):
        p = self.p
        with pytest.raises(ValueError):
            p.append("GDP", text=str(), required_units="yoy")

    def test_cannot_add_undefined_unit(self):
        p = self.p
        with pytest.raises(ValueError):
            p.append("NEWVAR", text=str(),
                     required_units="this_unit_doesnot_exit")

    def test_apend_after_append(self):
        p = self.p
        p.append(varname="INDPRO",
                 text="Индекс промышленного производства",
                 required_units=["yoy", "rog"],
                 desc="Промышленное производство")


class Mock:

    main = Definition()
    main.append(varname="GDP",
                text=["Oбъем ВВП",
                      "Индекс физического объема произведенного ВВП, в %"],
                required_units=["bln_rub", "yoy"],
                desc="Валовый внутренний продукт (ВВП)"
                #, sample="1999	4823	901	1102	1373	1447"
                )
    main.append(varname="INDPRO",
                text="Индекс промышленного производства",
                required_units=["yoy", "rog"],
                desc="Промышленное производство")

    @classmethod
    def pdef(cls):
        return cls.main


class Test_Definition:

    main = Mock.pdef()

    def test_public_attribs_are_callable(self):
        assert isinstance(self.main.varnames_dict, odict)
        assert isinstance(self.main.units_dict, odict)
        assert self.main.funcname is False
        assert isinstance(self.main.required, list)

    def test_scope_is_not_defined(self):
        assert self.main.get_bounds(rows=["more lines here",
                                          "more lines here"]) is False

    def test_get_varnames_is_callable(self):
        assert isinstance(self.main.get_varnames(), list)

    def test_repr(self):
        assert repr(self.main)


class Test_Scope:
    sc = Scope("Header 1", "Header 2")
    ah = "A bit rotten Header #1", "Curved Header 2."
    sc.add_bounds(*ah)
    row_mock = [ah[0],
                "more lines here",
                "more lines here",
                "more lines here",
                ah[1]]

    def test_repr(self):
        assert repr(self.sc)

    def test_able_to_find_bounds(self):
        s, e = self.sc.get_bounds(self.row_mock)
        assert s, e == self.ah


class Test_Specification:
    def test_public_getter_methods_are_callable(self):
        from csv2df.specification import SPEC
        assert SPEC.get_main_parsing_definition()
        assert SPEC.get_segment_parsing_definitions()

    def test_get_varnames(self):
        from csv2df.specification import SPEC
        assert SPEC.get_varnames()


if __name__ == "__main__":
    pytest.main([__file__])
