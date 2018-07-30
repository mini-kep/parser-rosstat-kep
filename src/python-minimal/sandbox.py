CSV_TEXT = """	Год / Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
1.2. Индекс промышленного производства1) / Industrial Production index1)																	
в % к соответствующему периоду предыдущего года / percent of corresponding period of previous year																	
2015	99,2	99,9	98,3	99,5	99,1	100,0	98,2	101,2	98,2	97,6	99,1	98,5	100,2	99,7	98,4	101,0	98,1
в % к предыдущему периоду / percent of previous period																	
2015		82,8	102,6	103,9	112,3	73,9	99,8	112,5	95,6	97,6	103,2	100,5	101,4	103,1	105,0	101,9	109,1
период с начала отчетного года в % к соответствующему периоду предыдущего года / period from beginning of reporting year as percent of corresponding period of previous year																	
2015						100,0	99,1	99,9	99,4	99,1	99,1	99,0	99,1	99,2	99,1	99,3	99,2
3.5. Индекс потребительских цен (на конец периода, в % к концу предыдущего периода) / Consumer Price Index (end of period, percent of end of previous period)																	
1999	136,5	116,0	107,3	105,6	103,9	108,4	104,1	102,8	103,0	102,2	101,9	102,8	101,2	101,5	101,4	101,2	101,3
в том числе: / of which:																	
продукты питания / food products																	
1999	135,0	118,4	106,4	104,3	102,8	110,4	104,4	102,7	102,5	102,0	101,8	103,3	100,3	100,7	100,7	100,9	101,2
	Год Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
алкогольные напитки / alcoholic beverages																	
1999	143,2	118,2	106,8	106,0	107,1	109,7	104,2	103,4	103,4	101,8	101,4	102,1	101,9	102,0	101,9	102,2	102,8
	Год Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
непродовольственные товары / non-food products																	
1999	139,2	114,0	108,6	107,2	104,9	106,2	104,0	103,2	104,0	102,7	101,6	101,9	102,4	102,7	102,2	101,5	101,1
	Год Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
услуги / services																	
1999	134,0	109,5	109,0	107,2	104,7	104,1	103,2	101,9	103,1	102,1	103,5	103,1	101,9	102,0	102,0	101,7	100,9
	Год1) Year1)	Кварталы1) / Quarters1)	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
		I	II	III	IV												
4. Социальная сфера / Social field	
2.2. Сальдированный финансовый результат1) по видам экономической деятельности, млн.рублей / Balanced financial result by economic activity, mln rubles												
Добыча полезных ископаемых / Mining and quarrying												
2017	2595632	258752	431071	582484	786597	966414	1288872	1488124	1676187	1890266	2124278	2384759
2018		340136	502726	840956								
Обрабатывающие производства / Manufacturing												
2017	2902753	109158	328302	603088	879688	1055179	1339108	1510626	1788974	2122127	2457117	2703476
2018		201347	368925	634681								
	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Убыточные организации
"""

INTRUCTIONS_DOC = """
- var: INDPRO
- headers: Индекс промышленного производства
- units: 
    - yoy
    - rog
    - ytd
- trail_down_names
- any:
    - INDPRO_yoy a 2015 99.2
    - INDPRO_rog q 2015 3 82.8
    - INDPRO_ytd m 2015 1 100    
---
- start_with: '3.5. Индекс потребительских цен'
- end_with: '4. Социальная сфера'
- var: CPI_NONFOOD
- headers: 
  - 'непродовольственные товары'
  - 'непродовольст- венные товары'
- force_units: rog
- all: 
    - CPI_NONFOOD_rog m 1999 12 101.1
---
- start_with: '2.2. Сальдированный финансовый результат'
- end_with: 'Убыточные организации'
- var: PROFIT_MINING
- headers: Добыча полезных ископаемых
- force_units: 'mln_rub'
- force_format: 'fiscal'
- all: 
    - PROFIT_MINING_mln_rub a 2017 2595632
"""   
# TODO: must deaccumulate PROFIT_MINING and similar


UNITS_DOC =  """
bln_usd :
  - млрд.долл.  
  - млрд.долларов
  - млрд. долларов
  - млрд, долларов
bln_rub :
  - млрд.руб.  
  - млрд.рублей
  - млрд. рублей
mln_rub :
  - млн.руб.  
rub : 
  - руб.
  - рублей
bln_tkm :
  - млрд.тонно-км
  - млрд. тонно-км
mln_t :
  - млн.тонн  
gdp_percent :    
  - в % к ВВП
mln :
  - млн
rog : 
  - '% к пред. периоду'
  - 'в % к прошлому периоду'
  - 'в % к предыдущему месяцу'
  - 'в % к предыдущему периоду'
  - '% к концу предыдущего периода'
  - 'в % к предыдущему периоду (в сопоставимых ценах)'
yoy :
  - '% год к году'
  - 'в % к соответствующему периоду предыдущего года (в сопоставимых ценах)'
  - 'в % к соответствующему периоду предыдущего года'
ytd : 
  - период с начала года
  - 'период с начала отчетного года в % к соответствующему периоду предыдущего года' 
"""


if __name__ == '__main__':    
    from kep.session import Session 
    s = Session(UNITS_DOC, INTRUCTIONS_DOC) 
    c = s.parse_tables(CSV_TEXT)
    assert len(c.datapoints()) == 77