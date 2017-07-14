# -*- coding: utf-8 -*-
"""Parsing instruction contains:
       - text to match with variable name
       - required variable names
       - csv line boundaries (optional)
       - reader function name for unusual table formats (optional)"""

from collections import OrderedDict as odict

class Units:
    
    glob = odict([# 1. MONEY
               ('млрд.долларов', 'bln_usd'),
               ('млрд. долларов', 'bln_usd'),
               ('млрд, долларов', 'bln_usd'),
               ('млрд.рублей', 'bln_rub'),
               ('млрд. рублей', 'bln_rub'),
               ('рублей / rubles', 'rub'),
               ('млн.рублей', 'mln_rub'),
               # 2. OTHER UNITS
               ('%', 'pct'),               
               ('в % к ВВП', 'gdp_percent'),
               # 3. RATES OF CHANGE
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
               # 4. stub for CPI section
               ("продукты питания", 'rog'),
               ("алкогольные напитки", 'rog'),
               ("непродовольственные товары", 'rog'),
               ("непродовольст- венные товары", 'rog'),
               ("услуги", 'rog')               
               ])
    
    names = {'bln_rub': 'млрд.руб.',
              'bln_usd': 'млрд.долл.',
              'gdp_percent': '% ВВП',
              'mln_rub': 'млн.руб.',
              'rub': 'руб.',
              'rog': '% к пред. периоду',
              'yoy': '% год к году',
              'ytd': 'период с начала года',
              'pct': '%'}
    
    # check: all units have a common short name
    assert set(names.keys()) == set(glob.values())    

    @staticmethod 
    def get_mapper_dict(required_units):
        return odict([(k,v) for k,v in Units.glob.items() 
                      if v in required_units])
    
    
class Definition():
    def __init__(self, text, varname, required_units, desc):
        # declarations
        self.headers = odict()
        # initialisation
        self.varname = varname        
        self.add_header(text)
        if isinstance(required_units, str):
            required_units = [required_units]
        self.units = Units.get_mapper_dict(required_units)           
        self.desc = desc
        
    def add_header(self, text):
        # linking parts of table header text ("Объем ВВП") to variable name ("GDP")
        self.headers.update(odict({text: self.varname}))
        return self
    
    def __required_units(self):
       return list(set(self.units.values()))
                   
    @property 
    def required(self):
        return [(self.varname, unit) for unit in self.__required_units()]
            
    def __repr__(self):
        text = [x for x in d.headers.keys()][0]
        ru = self.__required_units()
        #FIXME: no additional defintions
        return "Definition ('{}', '{}', {})".format(text, self.varname, ru)

class Scope():
    """Start and end lines for CSV file segment. 
    
       Hold several versions of start and end line, return applicable line 
       for a particular CSV file versions.
       
       Solves problem of different headers for same table at various releases.       
    """
    
    def __init__(self, start, end):        
        self.__markers = []
        self.add_bounds(start, end)
        self.definitions = []        
   
    def add_bounds(self, start, end):        
        if start and end:
            self.__markers.append(dict(start=start, end=end))
        else:
            raise ValueError("Cannot accept empty line as Scope() boundary")
   
    def append(self, text, varname, required_units, desc=""):
        pdef = Definition(text, varname, required_units, desc)
        self.definitions.append(pdef)

    def __repr__(self):
        vns = ", ".join([pdef.varname for pdef in self.definitions])
        msg1 = "Scope for varibales <{}>".format(vns)
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
      
        
if __name__ == "__main__": 
    
    main=[]
    d = Definition(text="Oбъем ВВП", 
                   varname="GDP", 
                   required_units=["bln_rub", "yoy"],                
                   desc="Валовый внутренний продукт")    
    d.add_header("Индекс физического объема произведенного ВВП, в %")
    # test code     
    assert d.required == [('GDP', 'bln_rub'), ('GDP', 'yoy')]
    assert d.headers == odict([('Oбъем ВВП', 'GDP'),                                            
             ('Индекс физического объема произведенного ВВП, в %', 'GDP')])
    assert 'bln_rub' in d.units.values()
    assert 'yoy' in d.units.values()
    # end-test-code 
    main.append(d)
    
    segments = []
    sc = Scope("1.9. Внешнеторговый оборот – всего",
               "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
    sc.add_bounds("1.10. Внешнеторговый оборот – всего",
                  "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")    
    sc.append(text="экспорт товаров – всего", 
              varname="EXPORT_GOODS", 
              required_units="bln_usd",                
              desc="Экспорт товаров")
    sc.append(text="импорт товаров – всего", 
              varname="IMPORT_GOODS", 
              required_units="bln_usd",                
              desc="Импорт товаров")   
    segments.append(sc)    

    # test code 
    sc = Scope("Header 1", "Header 2")    
    ah = "A bit rotten Header #1", "Curved Header 2."
    sc.add_bounds(*ah)
    d1 = dict(text="экспорт товаров – всего", 
              varname="EXPORT_GOODS", 
              required_units="bln_usd",                
              desc="Экспорт товаров")
    sc.append(**d1)    
    assert repr(sc)
    assert isinstance(sc.definitions, list)
    assert isinstance(sc.definitions[0], Definition)
    
    row_mock1 = ["A bit rotten Header #1",
     "more lines here", 
     "more lines here", 
     "more lines here",  
     "Curved Header 2."]
    s, e = sc.get_bounds(row_mock1)
    assert s, e == ah     
    # end-test-code    
     

    SPEC = dict(main=main, segments=segments)
    
    # test_code
    assert isinstance(SPEC, dict)    
    
    
    # TODO:
    # - [ ] add some more test asserts to Definition, Scope and SPEC 
    # - [ ] more assetrts to to test_cfg.py
    # - [ ] use new definitions in tables.py
    # - [ ] migrate existing definitions to this file
    # NOT TODO:
    # - [ ] think of a better pattern to create SPEC
    # - [ ] separate may cfg.py into definition.py (code, testable) and spec.py (values)    
