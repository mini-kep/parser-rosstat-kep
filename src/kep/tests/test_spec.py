# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict as odict

# testing
from kep.spec import Indicator, Definition, Scope, Specification


class Test_Indicator:

    i = Indicator(varname="GDP",
                  text=["Oбъем ВВП",
                        "Индекс физического объема произведенного ВВП, в %"],
                  required_units=["bln_rub", "yoy"],
                  desc="Валовый внутренний продукт")

    def test_repr(self):
        assert repr(self.i)

    def test_attributes(self):
        assert self.i.varname == "GDP"
        assert self.i.headers == odict(
            [('Oбъем ВВП', 'GDP'), ('Индекс физического объема произведенного ВВП, в %', 'GDP')])
        assert self.i.required == [('GDP', 'bln_rub'), ('GDP', 'yoy')]
        # end


class Test_Definition:

    main = Definition()
    main.append(varname="GDP",
                text=["Oбъем ВВП",
                      "Индекс физического объема произведенного ВВП, в %"],
                required_units=["bln_rub", "yoy"],
                desc="Валовый внутренний продукт (ВВП)",
                sample="1999	4823	901	1102	1373	1447")
    main.append(varname="INDPRO",
                text="Индекс промышленного производства",
                required_units=["yoy", "rog"],
                desc="Промышленное производство")

    def test_repr(self):
        assert repr(self.main)

    def test_headers(self):
        assert isinstance(self.main.headers, odict)


class Test_Scope:
    sc = Scope("Header 1", "Header 2")
    ah = "A bit rotten Header #1", "Curved Header 2."
    sc.add_bounds(*ah)
    sc.append(text="экспорт товаров",
              varname="EX",
              required_units="bln_usd",
              desc="Экспорт товаров")
    row_mock = [ah[0],
                "more lines here",
                "more lines here",
                "more lines here",
                ah[1]]

    def test_repr(self):
        assert repr(self.sc)

    def test_def(self):
        assert isinstance(self.sc.definition, Definition)

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
