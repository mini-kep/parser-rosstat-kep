# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict as odict

# testing
from kep.spec import ParsingInstruction, Definition, Scope, Specification


class Test_ParsingInstruction:

    p = ParsingInstruction()
    p.append(varname="GDP",
                  text=["Oбъем ВВП",
                        "Индекс физического объема произведенного ВВП, в %"],
                  required_units=["bln_rub", "yoy"],
                  desc="Валовый внутренний продукт")

    def test_attributes(self):
        assert self.p.varname_mapper == odict(
            [('Oбъем ВВП', 'GDP'), ('Индекс физического объема произведенного ВВП, в %', 'GDP')])
        assert self.p.required_labels == [('GDP', 'bln_rub'), ('GDP', 'yoy')]
        assert self.p.descriptions == odict({"GDP":"Валовый внутренний продукт"})


class Test_Definition:

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

    def test_repr(self):
        assert repr(self.main)

    def test_get_methods(self):
        assert isinstance(self.main.get_varnames(), list)
        assert isinstance(self.main.get_required_labels(), list)


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
    # TODO:
    # test_code
    #assert isinstance(SPEC, Specification)
    #assert isinstance(SPEC.main, Definition)
    #assert SPEC.main.headers
    #assert SPEC.main.required
    #assert SPEC.main.reader is None
    # for scope in SPEC.scopes:
    #    assert isinstance(scope.definition, Definition)
    pass


if __name__ == "__main__":
    pytest.main([__file__])
