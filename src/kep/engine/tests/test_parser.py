from kep.engine.parser import extract_unit, iterate
import pytest


units_dict = {
    'млрд.рублей': 'bln_rub',
    'в % к соответствующему периоду предыдущего года': 'yoy'
}


@pytest.mark.parametrize('unit, text', [
    ['bln_rub', 'abc - млрд.рублей'],
    ['yoy', 'в % к соответствующему периоду предыдущего года '
            '/ percent of corresponding period of previous year']
])
def test_extract_unit(unit, text):
    assert unit == extract_unit(text, units_dict)


def test_iterate():
    assert iterate('abc') == ['abc']


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
name: INDPRO
headers: Индекс промышленного производства
units:
    - yoy
    - rog
    - ytd
---
start_with: '3.5. Индекс потребительских цен'
end_with: '4. Социальная сфера'
commands:
    - name: CPI_NONFOOD
      headers:
      - 'непродовольственные товары'
      - 'непродовольст- венные товары'
      units: rog
      force_units: true
---
start_with: '2.2. Сальдированный финансовый результат'
end_with: 'Убыточные организации'
commands:
    - name: PROFIT_MINING
      headers: Добыча полезных ископаемых
      units: 'mln_rub'
      force_units: true
      row_format: 'fiscal'
"""

UNITS_DOC = """
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

import kep.parameters
from kep.engine.row import Datapoint
from kep.engine.reader import read_tables
from kep.engine.parser import parse_tables, labels, datapoints
from kep.utilities import TempFile

with TempFile(UNITS_DOC) as units_filepath:
    units_dict = kep.parameters.get_mapper(units_filepath)

with TempFile(INTRUCTIONS_DOC) as instructions_filepath:
    common_dicts = kep.parameters.read_by_key(instructions_filepath, 'name')
    segment_dicts = kep.parameters.read_by_key(
        instructions_filepath, 'start_with')

with TempFile(CSV_TEXT) as csv_filepath:
    tables = read_tables(csv_filepath)

parsed_tables = parse_tables(tables, common_dicts, segment_dicts, units_dict)
datapoints = datapoints(parsed_tables)


class Test_parsed_tables():
    def test_lables(self):
        assert labels(parsed_tables) == [('INDPRO', 'yoy'),
                                         ('INDPRO', 'rog'),
                                         ('INDPRO', 'ytd'),
                                         ('CPI_NONFOOD', 'rog'),
                                         ('PROFIT_MINING', 'mln_rub')]

    def test_datapoint_method(self):
        assert len(datapoints) == 77

    def test_datapoint_mathces_exactly(self):
        assert datapoints == [
            Datapoint(label='INDPRO_yoy', freq='a', year=2015, month=12, value=99.2),
            Datapoint(label='INDPRO_yoy', freq='q', year=2015, month=3, value=99.9),
            Datapoint(label='INDPRO_yoy', freq='q', year=2015, month=6, value=98.3),
            Datapoint(label='INDPRO_yoy', freq='q', year=2015, month=9, value=99.5),
            Datapoint(label='INDPRO_yoy', freq='q', year=2015, month=12, value=99.1),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=1, value=100.0),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=2, value=98.2),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=3, value=101.2),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=4, value=98.2),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=5, value=97.6),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=6, value=99.1),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=7, value=98.5),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=8, value=100.2),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=9, value=99.7),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=10, value=98.4),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=11, value=101.0),
            Datapoint(label='INDPRO_yoy', freq='m', year=2015, month=12, value=98.1),
            Datapoint(label='INDPRO_rog', freq='q', year=2015, month=3, value=82.8),
            Datapoint(label='INDPRO_rog', freq='q', year=2015, month=6, value=102.6),
            Datapoint(label='INDPRO_rog', freq='q', year=2015, month=9, value=103.9),
            Datapoint(label='INDPRO_rog', freq='q', year=2015, month=12, value=112.3),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=1, value=73.9),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=2, value=99.8),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=3, value=112.5),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=4, value=95.6),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=5, value=97.6),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=6, value=103.2),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=7, value=100.5),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=8, value=101.4),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=9, value=103.1),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=10, value=105.0),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=11, value=101.9),
            Datapoint(label='INDPRO_rog', freq='m', year=2015, month=12, value=109.1),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=1, value=100.0),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=2, value=99.1),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=3, value=99.9),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=4, value=99.4),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=5, value=99.1),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=6, value=99.1),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=7, value=99.0),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=8, value=99.1),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=9, value=99.2),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=10, value=99.1),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=11, value=99.3),
            Datapoint(label='INDPRO_ytd', freq='m', year=2015, month=12, value=99.2),
            Datapoint(label='CPI_NONFOOD_rog', freq='a', year=1999, month=12, value=139.2),
            Datapoint(label='CPI_NONFOOD_rog', freq='q', year=1999, month=3, value=114.0),
            Datapoint(label='CPI_NONFOOD_rog', freq='q', year=1999, month=6, value=108.6),
            Datapoint(label='CPI_NONFOOD_rog', freq='q', year=1999, month=9, value=107.2),
            Datapoint(label='CPI_NONFOOD_rog', freq='q', year=1999, month=12, value=104.9),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=1, value=106.2),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=2, value=104.0),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=3, value=103.2),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=4, value=104.0),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=5, value=102.7),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=6, value=101.6),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=7, value=101.9),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=8, value=102.4),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=9, value=102.7),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=10, value=102.2),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=11, value=101.5),
            Datapoint(label='CPI_NONFOOD_rog', freq='m', year=1999, month=12, value=101.1),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='a', year=2017, month=12, value=2595632.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=1, value=258752.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=2, value=431071.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=3, value=582484.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=4, value=786597.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=5, value=966414.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=6, value=1288872.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=7, value=1488124.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=8, value=1676187.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=9, value=1890266.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=10, value=2124278.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2017, month=11, value=2384759.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2018, month=1, value=340136.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2018, month=2, value=502726.0),
            Datapoint(label='PROFIT_MINING_mln_rub', freq='m', year=2018, month=3, value=840956.0)]
