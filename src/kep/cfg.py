# -*- coding: utf-8 -*-
from pathlib import Path
from collections import OrderedDict as odict   

# csv file parameters
ENC = 'utf8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')


# folder structure
"""
\data
  \raw      
      \word
  \interim
      \2017          
  \processed
      \latest
      \2017
      \...
"""
me = Path(__file__)
levels_up = 2
data_folder = me.parents[levels_up] / 'data' 
rosstat_folder = data_folder / 'interim'
csv_path = rosstat_folder / "testdata.csv" 
PREFIX = ""#"ind"


# interim data
class DataLocation():
    
    def __init__(self, folder=rosstat_folder, prefix = PREFIX):
        self.folder = folder
        self.prefix = prefix
        self.dirs = self.listing(folder)

    def listing(self, _folder):
        return [f.name for f in _folder.iterdir() if f.is_dir()]
    
    def max_year(self):
        return max(self.dirs)
        
    def max_month(self):
        subfolder = self.folder / self.max_year()
        return max(self.listing(subfolder)).replace(self.prefix,"") 
    
    def get_latest(self):
        return int(self.max_year()), int(self.max_month())

def get_path_csv(year=None, month=None):
    """Return CSV file path based on year and month"""
    if not year and not month:
        year, month = DataLocation().get_latest()
    if year and month:
        month_dir = PREFIX+str(month).zfill(2)
        return rosstat_folder / str(year) / month_dir / 'tab.csv'
    
assert int(DataLocation().max_year()) >= 2017
mm = int(DataLocation().max_month())
assert mm <= 12 
assert mm >= 1 

# TODO: output directory locations

units = {'млрд.долларов': 'bln_usd',
             'млрд.рублей': 'bln_rub',
             "Индекс физического объема": 'rog',
             'в % к ВВП': 'gdp_percent',
             'в % к декабрю предыдущего года': 'ytd',
             'в % к предыдущему месяцу': 'rog',
             'в % к предыдущему периоду': 'rog',
             'в % к соответствующему месяцу предыдущего года': 'yoy',
             'в % к соответствующему периоду предыдущего года': 'yoy',
             'млн.рублей': 'mln_rub',
             'отчетный месяц в % к предыдущему месяцу': 'rog',
             'отчетный месяц в % к соответствующему месяцу предыдущего года': 'yoy',
             'период с начала отчетного года': 'ytd',
             'рублей / rubles': 'rub'}
    

exclude = ["IMPORT_GOODS__TOTAL_yoy", "IMPORT__GOODS_TOTAL_rog",
           "EXPORT_GOODS__TOTAL_yoy", "EXPORT__GOODS_TOTAL_rog"]
    
class Definition():    
    def __init__(self, name):        
        self.name = name
        self.headers = odict()        
        self.markers = []
        self.reader = None
        
    def add_header(self, text, varname):
        self.headers.update(odict({text: varname})) 

    def add_marker(self, _start, _end):
        self.markers.append(odict(start=_start, end=_end))
    
    def add_reader(self, funcname):
        self.reader = funcname
        
    def __str__(self):
        return self.name + "({})".format(len(self.headers))
    
    def __repr__(self):
        return self.__str__()
    
    def varnames(self):
        return list(set(v for v in self.headers.values()))

class Specification:
    def __init__(self, pdef_main):
        self.main = pdef_main
        self.additional = []
        
    def append(self, pdef):
        self.additional.append(pdef) 
        
    def validate(self):
        pass
        
    def varnames(self):
        vns = set()
        for pdef in [self.main] + self.additional:
            for x in pdef.varnames():
                vns.add(x)
        return list(vns)        
    
    # TODO validate specification - order of markers 
    # - ends are after starts
    # - sorted starts follow each other    
        
    def __str__(self): 
        msg1 = "<Default parsing definition: " + self.main.__str__()
        listing = ", ".join(d.__str__() for d in self.additional)
        msg2 = ", additional: [{}]. ".format(listing) 
        msg3 = "Total varnames: {}>".format(len(self.varnames())) 
        return msg1 + msg2 + msg3
    
        
        
d = Definition("MAIN")
d.add_header("Объем ВВП", "GDP")
d.add_header("Индекс физического объема произведенного ВВП, в %", "GDP")
d.add_header("Индекс промышленного производства", "IND_PROD")
# will be IND_PROD *n if no end specified
d.add_marker(None, "1.2.1. Индексы производства по видам деятельности")
spec = Specification(d)


d = Definition("EXIM")
d.add_marker("1.9. Внешнеторговый оборот – всего"
           , "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_marker("1.10. Внешнеторговый оборот – всего"
           , "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья")
d.add_header("экспорт товаров – всего", "EXPORT_GOODS_TOTAL")
d.add_header("импорт товаров – всего", "IMPORT_GOODS_TOTAL")
spec.append(d)


d = Definition("GOV_REVENUE_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.1. Доходы (по данным Федерального казначейства)"
           , "2.1.2. Расходы (по данным Федерального казначейства)")
d.add_header("Консолидированный бюджет", "GOV_REVENUE_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет",       "GOV_REVENUE_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_REVENUE_ACCUM_SUBFEDERAL")
spec.append(d)


d = Definition("GOV_EXPENSE_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.2. Расходы (по данным Федерального казначейства)"
           , "2.1.3. Превышение доходов над расходами")
d.add_header("Консолидированный бюджет", "GOV_EXPENSE_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет",       "GOV_EXPENSE_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_EXPENSE_ACCUM_SUBFEDERAL")
spec.append(d)


d = Definition("GOV_SURPLUS_ACCUM")
d.add_reader("fiscal")
d.add_marker("2.1.3. Превышение доходов над расходами"
           , "2.2. Сальдированный финансовый результат")
d.add_header("Консолидированный бюджет", "GOV_SURPLUS_ACCUM_CONSOLIDATED")
d.add_header("Федеральный бюджет",       "GOV_SURPLUS_ACCUM_FEDERAL")
d.add_header("Консолидированные бюджеты субъектов Российской Федерации", "GOV_SURPLUS_ACCUM_SUBFEDERAL")
spec.append(d)

# TODO: next segment
## segment information
#start line : 
#  - 1.13. Оборот розничной торговли, млрд.рублей
#  - 1.12. Оборот розничной торговли, млрд.рублей
#end line : 
#  - 1.13.1. Оборот общественного питания, млрд.рублей
#  - 1.12.1. Оборот общественного питания, млрд.рублей
#special reader: null
#
#
##1.13. Оборот розничной торговли, млрд.рублей           / Retail trade turnover, bln rubles
#
#Оборот розничной торговли :
#  - RETAIL_SALES
#  - bln_rub
#  - 1.13

##в % к соответствующему периоду предыдущего года (в сопоставимых ценах)  / percent of corresponding period of previous year (at constant prices)
##20141)
##в % к предыдущему периоду (в сопоставимых ценах) / percent of previous period (at constant prices)
#
##Из общего объема оборота розничной торговли:
##пищевые продукты, включая напитки, и табачные изделия1),  млрд.рублей / Of total volume of retail trade turnover: food products, including beverages, and tobacco1),
##bln rubles
#
#пищевые продукты, включая напитки, и табачные изделия : 
# - RETAIL_SALES_FOOD_INCBEV_AND_TABACCO
# - bln_rub 
#
#
##в % к соответствующему периоду предыдущего года (в сопоставимых ценах)  / percent of corresponding period of previous year (at constant prices)
##20142)
##в % к предыдущему периоду (в сопоставимых ценах)  / percent of previous period (at constant prices)
#
##непродовольственные товары1),   млрд.рублей  / non-food goods1),  bln rubles
## TODO:
#
#непродовольственные товары :
# - RETAIL_SALES_NONFOOD_GOODS
# - bln_rub 

spec.validate()
print("Current specification:", spec)

doc = """1. Сводные показатели / Aggregated indicators					
1.1. Валовой внутренний продукт1) / Gross domestic product1)					
Объем ВВП, млрд.рублей /GDP, bln rubles					
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044
2001	8944	1901	2105	2488	2450
2002	10831	2262	2529	3013	3027
2003	13208	2851	3102	3600	3655
2004	17027	3516	3972	4594	4945
2005	21610	4459	5078	5845	6228
2006	26917	5793	6368	7276	7480
2007	33248	6780	7768	8903	9797
2008	41277	8878	10238	11542	10619
2009	38807	8335	9245	10411	10816
2010	46308	9996	10977	12086	13249
2011	59698	12844	14314	15663	16877
2012	66927	14925	16149	17442	18411
2013	71017	15892	17015	18543	19567
20142)	79200	17139	18884	20407	21515
20152)	83233	18210	19284	21294	22016
20162)	85881	18561	19979	22190	
2017					
Индекс физического объема произведенного ВВП, в % / Volume index of produced GDP, percent					
1999	106,4	98,1	103,1	111,4	112,0
2000	110,0	111,4	110,2	110,5	108,2
2001	105,1	104,7	105,0	106,0	104,5
2002	104,7	103,8	104,4	104,4	106,2
2003	107,3	107,5	107,9	106,1	107,6
2004	107,2	107,2	108,0	107,3	106,2
2005	106,4	105,6	106,0	106,0	107,8
2006	108,2	107,3	108,1	108,2	108,9
2007	108,5	108,1	108,6	108,2	109,2
2008	105,2	109,2	107,9	106,4	98,7
2009	92,2	90,8	88,8	91,4	97,4
2010	104,5	104,1	105,0	103,8	105,1
2011	104,3	103,3	103,3	105,0	105,2
2012	103,5	105,3	104,3	103,1	101,8
2013	101,3	100,6	101,1	101,2	102,1
20142)	100,7	100,6	101,1	100,9	100,2
20152)	97,2	97,2	95,5	96,3	96,2
20162)	99,8	98,8	99,4	99,6	
2017					
	Год / Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
1.2. Индекс промышленного производства1) / Industrial Production index1)																	
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year																	
2015	99,2	99,9	98,3	99,5	99,1	100,0	98,2	101,2	98,2	97,6	99,1	98,5	100,2	99,7	98,4	101,0	98,1
2016	101,3	101,1	101,5	101,0	101,7	99,2	103,8	100,3	101,0	101,5	102,0	101,4	101,5	100,1	101,6	103,4	100,2
2017

1.9. Внешнеторговый оборот – всего1), млрд.долларов США / Foreign trade turnover – total1), bln US dollars																	
1999	115,1	24,4	27,2	28,4	35,1	7,2	7,9	9,3	9,8	8,0	9,3	9,5	9,3	9,6	10,4	11,1	13,7
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year																	
1999	86,9	68,1	75,5	87,0	125,3	63,5	68,3	72,1	80,5	68,6	77,0	78,4	83,7	102,2	117,9	127,4	129,8
в % к предыдущему периоду / percent of previous period																	
1999		87,0	111,5	104,3	123,9	68,1	109,5	118,0	105,7	81,5	116,7	101,8	97,4	103,2	108,2	106,9	123,9

в том числе:																	
экспорт товаров – всего, млрд.долларов США																	
/ of which: export of goods – total, bln US dollars																	
1999	75,6	15,3	17,1	18,9	24,3	4,5	4,9	5,8	6,6	5,1	5,4	6,3	6,2	6,4	7,0	7,6	9,7
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year																	
1999	101,5	85,1	91,6	98,5	130,1	79,0	86,8	89,0	106,4	84,9	83,8	94,4	99,8	101,5	119,0	132,3	137,5
в % к предыдущему периоду / percent of previous period																	
1999		81,7	111,9	110,5	128,8	63,7	109,5	118,3	112,4	78,3	105,1	116,4	98,2	104,4	108,4	109,0	127,9

импорт товаров – всего, млрд.долларов США																	
/ import of goods – total, bln US dollars																	
1999	39,5	9,1	10,1	9,5	10,8	2,7	3,0	3,5	3,3	2,9	4,0	3,2	3,1	3,1	3,4	3,5	4,0
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year																	
1999	68,1	51,1	58,1	70,6	115,8	47,8	50,3	54,7	54,2	51,0	69,3	58,9	63,4	103,5	115,7	117,7	114,3
в % к предыдущему периоду / percent of previous period																	
1999		97,4	110,9	93,8	114,2	77,0	109,7	117,6	94,5	87,8	137,3	81,9	96,0	100,9	107,7	102,5	115,3
1.9.1. Внешнеторговый оборот со странами дальнего зарубежья – всего, млрд.долларов США / Foreign trade turnover with far abroad countries – total, bln US dollars

2.1.1. Доходы (по данным Федерального казначейства)1) / Revenues (data of the Federal Treasury)1)												
Консолидированный бюджет, млрд.рублей / Consolidated budget, bln rubles												
20142)	26766,1	1726,3	3579,8	5960,4	8498,3	10572,3	12671,2	15108,2	17143,4	19221,4	21563,5	23439,4
________________________ 1) Данные по консолидированному бюджету за 2005г. и, начиная с I полугодия 2006г., приведены с учетом бюджетов государственных внебюджетных фондов. / 2005 data and data starting 1st half year of 2006 on consolidated budget are given taking into account budgets of public non-budget funds. 2) Начиная с I квартала 2014г. данные об исполнении бюджета приведены с учетом сведений по Республике Крым и г.Севастополю. / Since the second half of 2014 the budget execution data are prepared using data of the Crimea and city of Sevastopol. 3) Оперативные данные. / Short-term data.												
Федеральный бюджет, млрд.рублей / Federal budget, bln rubles												
2014	14496,9	1326,7	2368,6	3521,4	4754,3	5882,6	7120,9	8255,7	9439,6	10698,3	11891,6	12951,4
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles												
2014	8905,7	295,6	863,1	1790,6	2840,5	3493,1	4052,1	5067,5	5704,7	6325,4	7246,1	7834,5


2.1.2. Расходы (по данным Федерального казначейства)1) / Expenditures (data of the Federal Treasury)1)												
Консолидированный бюджет, млрд.рублей / Consolidated budget, bln rubles												
2016	30888,82)	1095,5	3348,6	6339,1	9029,5	11106,6	13582,9	15784,1	18101,9	20493,6	22875,3	25444,1
Федеральный бюджет, млрд.рублей / Federal budget, bln rubles												
2014	14831,6	761,2	2261,5	3345,7	4626,2	5406,4	6402,1	7516,5	8467,4	9529,0	10713,9	11639,2
	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles												
2014	9353,3	405,8	1010,4	1683,2	2501,7	3192,2	3961,9	4758,5	5421,7	6150,4	7023,1	7769,5
	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov

"2.1.3. Превышение доходов над расходами /профицит /, расходов над доходами /дефицит "" - ""/ (по данным Федерального казначейства) / Surplus of revenues over expenditures /proficit/, surplus of expenditures over revenues /deficit ‘-‘/ (data of the Federal Treasure)"												
Федеральный бюджет, млрд.рублей / Federal budget, bln rubles												
2014	-334,7	565,5	107,0	175,7	128,1	476,2	718,8	739,1	972,3	1169,3	1177,7	1312,2
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles												
2014	-447,6	-110,2	-147,4	107,4	338,8	300,8	90,2	308,9	283,0	175,0	222,9	65,0
	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
2.2. Сальдированный финансовый результат1) по видам экономической деятельности, млн.рублей / Balanced financial result by economic activity, mln rubles												
"""
   
Path(csv_path).write_text(doc, encoding=ENC)



