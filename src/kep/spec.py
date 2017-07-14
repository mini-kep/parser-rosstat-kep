# -*- coding: utf-8 -*-
"""Parsing instruction contains:
       - text to match with variable name
       - required variable names
       - csv line boundaries (optional)
       - reader function name for unusual table formats (optional)"""

from collections import OrderedDict as odict


UNITS = odict([# 1. MONEY
               ('млрд.долларов', 'bln_usd'),
               ('млрд. долларов', 'bln_usd'),
               ('млрд, долларов', 'bln_usd'),
               ('млрд.рублей', 'bln_rub'),
               ('млрд. рублей', 'bln_rub'),
               ('рублей / rubles', 'rub'),
               ('млн.рублей', 'mln_rub'),
               # 2. RATES OF CHANGE
               ("Индекс физического объема произведенного ВВП, в %", 'yoy'),
               ('в % к декабрю предыдущего года', 'ytd'),
               ('в % к предыдущему месяцу', 'rog'),
               ('в % к предыдущему периоду', 'rog'),
               ('% к концу предыдущего периода', 'rog'),
               # this...
               ('период с начала отчетного года в % к соответствующему периоду предыдущего года', 'ytd'),
               #       ... must precede this
               # because 'в % к предыдущему периоду' is found in
               # 'период с начала отчетного года в % к соответствующему периоду предыдущего года'
               ('в % к соответствующему периоду предыдущего года', 'yoy'),
               ('в % к соответствующему месяцу предыдущего года', 'yoy'),
               ('отчетный месяц в % к предыдущему месяцу', 'rog'),
               ('отчетный месяц в % к соответствующему месяцу предыдущего года', 'yoy'),
               ('период с начала отчетного года', 'ytd'),                              
               # 3. OTHER UNITS (keep below RATES OF CHANGE)
               ('%', 'pct'),               
               ('в % к ВВП', 'gdp_percent'),               
               # 4. stub for CPI section
               ("продукты питания", 'rog'),
               ("алкогольные напитки", 'rog'),
               ("непродовольственные товары", 'rog'),
               ("непродовольст- венные товары", 'rog'),
               ("услуги", 'rog')               
               ])
    
UNIT_NAMES = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'rub': 'руб.',
              'rog': '% к пред. периоду',
              'yoy': '% год к году',
              'ytd': 'период с начала года',
              'pct': '%'}
    
# check: all units have a common short name
assert set(UNIT_NAMES.keys()) == set(UNITS.values())    


class Definition:
    
    def __init__(self, reader = None):
        self.definitions = []
        self.reader = reader
        
    def append(self, text, varname, required_units, desc):
        pdef = Indicator(text, varname, required_units, desc)
        self.definitions.append(pdef)
    
    @property    
    def headers(self):
        def _yield():
            for pdef in self.definitions:
                for k,v in pdef.headers.items():
                    yield k, v                    
        return odict(list( _yield()))
    
    @property  
    def required(self):
        def _yield():
            for pdef in self.definitions:
                for req in pdef.required:
                    yield req
        return list(_yield())    
    
    def varnames(self):
        return [pdef.varname for pdef in self.definitions]         
    
    def __repr__(self):
        vns = ", ".join(self.varnames())
        return "<Definition for {}>".format(vns)    
    
class Indicator:
    
    def __init__(self, text, varname, required_units, desc):
        self.varname = varname        
        text = self.as_list(text)
        self.headers = odict([(t, self.varname) for t in text])      
        ru = self.as_list(required_units)
        self.required = [(self.varname, unit) for unit in ru]
        self.desc = desc                   
           
    def __repr__(self):
        text = [x for x in d.headers.keys()]
        ru = [x[1] for x in self.required]
        return "Definition ('{}', {}, {}, '{}')".format(self.varname, text, 
                                                        ru, self.desc)
    @staticmethod
    def as_list(x):
       if isinstance(x, str):
           return [x]
       else:
           return x    
        
class Scope():
    """Start and end lines for CSV file segment and associated variables 
       defintion.
    
       Holds several versions of start and end line, return applicable line 
       for a particular CSV file versions. This solves problem of different 
       headers for same table at various releases.       
    """
    
    def __init__(self, start, end, reader=None):        
        self.__markers = []
        self.add_bounds(start, end)
        self.definition = Definition(reader)
   
    def add_bounds(self, start, end):        
        if start and end:
            self.__markers.append(dict(start=start, end=end))
        else:
            raise ValueError("Cannot accept empty line as Scope() boundary")
   
    def append(self, text, varname, required_units, desc):
        self.definition.append(text, varname, required_units, desc)

    def __repr__(self):        
        msg1 = repr(self.definition)
        s = self.__markers[0]['start'][:8]
        e = self.__markers[0]['end'][:8]
        msg2 = "bound by start <{}...>, end <{}...>".format(s, e)
        return " ".join([msg1, msg2])
        
    def get_bounds(self, rows):
        """Get start and end line markers, which aplly to *rows*"""
        rows = [r for r in rows] # consume iterator
        ix = False
        for i, marker in enumerate(self.__markers):
            s = marker['start']
            e = marker['end']            
            if self.__is_found(s, rows) and self.__is_found(e, rows):
               m = self.__markers[ix]
               return m['start'], m['end']
        if not ix:
            msg = self.__error_message(rows)  
            raise ValueError(msg)           

    @staticmethod        
    def __is_found(line, rows):
        """Return True, is *line* found at start of any entry in *rows*""" 
        for r in rows:
            if r.startswith(line):
                return True
        return False 

    def __error_message(self, rows):
        msg = []
        msg.append("start or end line not found in *rows*")
        for marker in self.markers:
            s = marker['start']
            e = marker['end']
            msg.append("is_found: {} <{}>".format(self.__is_found(s, rows), s))
            msg.append("is_found: {} <{}>".format(self.__is_found(e, rows), e))
        return "\n".join(msg)


class Specification:
    """Specification holds a list of defintions in two variables:
        
       .main (default definition)
       .additional (segment defintitions)
    """

    def __init__(self, pdef):
        self.main = pdef
        self.scopes = []
        
    def all_definitions(self):
        return [self.main] + [sc.definition for sc in self.scopes]

    def append(self, scope):
        self.scopes.append(scope)

    def varnames(self):
        varnames = set()
        for pdef in self.all_definitions():
            for x in pdef.varnames():
                varnames.add(x)
        return sorted(list(varnames))

    def validate(self, rows):
        # TODO: validate specification - order of markers
        # - ends are after starts
        # - sorted end-starts follow each other
        pass

    def required(self):
        for pdef in self.all_definitions():
            for req in pdef.required:
                yield req

main = Definition()
main.append(varname="GDP",
            text=["Oбъем ВВП",
                  "Индекс физического объема произведенного ВВП, в %",   
                  "Валовой внутренний продукт"],
            required_units=["bln_rub", "yoy"],                
            desc="Валовый внутренний продукт")    
main.append(varname="INDPRO",
            text="Индекс промышленного производства",
            required_units=["yoy", "rog"],
            desc="Индекс промышленного производства") 
    
SPEC = Specification(main)

seg = Scope("1.9. Внешнеторговый оборот – всего",
           "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
seg.add_bounds("1.10. Внешнеторговый оборот – всего",
              "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")    
seg.append(text="экспорт товаров – всего", 
          varname="EXPORT_GOODS", 
          required_units="bln_usd",                
          desc="Экспорт товаров")
seg.append(text="импорт товаров – всего", 
          varname="IMPORT_GOODS", 
          required_units="bln_usd",                
          desc="Импорт товаров")   
SPEC.append(seg)    


seg = Scope(start="3.5. Индекс потребительских цен",
              end="4. Социальная сфера")
seg.append(text="Индекс потребительских цен", 
           varname="CPI", 
           required_units="rog",                
           desc="Индекс потребительских цен (ИПЦ)")
seg.append(text=["непродовольственные товары", 
                 "непродовольст- венные товары"],
           varname="CPI_NONFOOD", 
           required_units="rog",                
           desc="ИПЦ (непродтовары)")
seg.append(text="продукты питания", 
           varname="CPI_FOOD", 
           required_units="rog",                
           desc="ИПЦ (продтовары)")
seg.append(text="алкогольные напитки", 
           varname="CPI_ALC", 
           required_units="rog",                
           desc="ИПЦ (алкоголь)")
seg.append(text="услуги", 
           varname="CPI_SERVICES", 
           required_units="rog",                
           desc="ИПЦ (услуги)")
SPEC.append(seg)

        
if __name__ == "__main__": 
    # test code  
    d = Indicator(varname="GDP", 
                  text=["Oбъем ВВП", 
                        "Индекс физического объема произведенного ВВП, в %"],
                  required_units=["bln_rub", "yoy"],                
                  desc="Валовый внутренний продукт")   
    assert repr(d)
    assert d.varname =="GDP"
    assert d.headers == odict([('Oбъем ВВП', 'GDP'),                                            
             ('Индекс физического объема произведенного ВВП, в %', 'GDP')])
    assert d.required == [('GDP', 'bln_rub'), ('GDP', 'yoy')]
    # end
    

    # test code
    assert repr(main)
    assert isinstance(main.headers, odict)
    # end
    

    # test code 
    sc = Scope("Header 1", "Header 2")    
    ah = "A bit rotten Header #1", "Curved Header 2."
    sc.add_bounds(*ah)
    sc.append(text="экспорт товаров", 
              varname="EX", 
              required_units="bln_usd",              
              desc="Экспорт товаров")
    assert repr(sc)
    assert isinstance(sc.definition, Definition)
    
    row_mock1 = ["A bit rotten Header #1",
     "more lines here", 
     "more lines here", 
     "more lines here",  
     "Curved Header 2."]
    s, e = sc.get_bounds(row_mock1)
    assert s, e == ah     
    # end
     

    
    # test_code
    assert isinstance(SPEC, Specification) 
    assert isinstance(SPEC.main, Definition)
    assert SPEC.main.headers
    assert SPEC.main.required
    assert SPEC.main.reader is None
    for scope in SPEC.scopes:
        assert isinstance(scope.definition, Definition)
    # end
    
    
    # TODO:
    # - [ ] add some more test asserts to Definition, Scope and SPEC 
    # - [ ] more assetrts to to test_cfg.py
    # - [ ] use new definitions in tables.py
    # - [ ] migrate existing definitions to this file
    # NOT TODO:
    # - [ ] think of a better pattern to create SPEC
    # - [ ] separate may cfg.py into definition.py (code, testable) and spec.py (values)    