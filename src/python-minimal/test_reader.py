from collections import OrderedDict
from pathlib import Path


import reader 
from parsing_definition import UNITS, Namer
from dev_helper import PATH


#EP: вместо PATH сделать фикстуру, которая будет предосталвлять файл CSV с гарантированным путем к нему? 
#EP: надо ли изолировать UNITS?

class Test_emit_datapoints:
    def test_on_YAQQQ(self):
        param = dict(
            row=["1999", "4823", "901", "1102", "1373", "1447"],
            label="GDP_bln_rub",
            row_format="YAQQQQ",
        )
        result = reader.emit_datapoints_from_row(**param)
        assert list(result) == [
            dict(label="GDP_bln_rub", freq="a", date='1999-12-31', value=4823),
            dict(label="GDP_bln_rub", freq="q", date='1999-03-31', value=901),
            dict(label="GDP_bln_rub", freq="q", date='1999-06-30', value=1102),
            dict(label="GDP_bln_rub", freq="q", date='1999-09-30', value=1373),
            dict(label="GDP_bln_rub", freq="q", date='1999-12-31', value=1447),
        ]

    def test_on_YA12M(self):
        param = dict(
            row=["2015", "94,6", "91,4", "110,9", "96,2", "102,7", "98,0", "103,4",
                                 "100,9", "99,1", "103,9", "95,9", "104,2", ],
            label="MINING_rog",
            row_format="YMMMMMMMMMMMM",
        )
        dps = list(reader.emit_datapoints_from_row(**param))
        assert dps[0] == {
            "label": "MINING_rog",
            "freq": "m",
            "date": '2015-01-31',
            "value": 94.6,
        }
        assert dps[11] == {
            "label": "MINING_rog",
            "freq": "m",
            "date": '2015-12-31',
            "value": 104.2,
        }


def test_parsed_tables_on_csv_file_and_simple_units_and_namer():
    unit_mapper_dict1 = OrderedDict(
        [
            ("млрд.рублей", "bln_rub"),
            # this ...
            ("период с начала отчетного года в % к соответствующему периоду предыдущего года",
             "ytd",
            ),
            # ... must precede this
            ("в % к соответствующему периоду предыдущего года", "yoy"),
            ("в % к предыдущему периоду", "rog"),
            ("отчетный месяц в % к предыдущему месяцу", "rog"),
        ]
    )
    namer1 = Namer(name="GDP", headers=["Объем ВВП"], units=["bln_rub"])
    tables = reader.parsed_tables(PATH, 
                                  unit_mapper_dict=unit_mapper_dict1, 
                                  namers=[namer1]
    )
    assert tables[0].name == "GDP"
    assert tables[0].unit == "bln_rub"
    assert tables[0].row_format == "YAQQQQ"
    assert tables[4].unit == "ytd"
    datapoints = [x for x in reader.emit_datapoints(tables)]
    assert datapoints[94] == {
        "freq": "q",
        "label": "GDP_bln_rub",
        "date": '2017-12-31',
        "value": 25503,
    }
    assert datapoints[0] == {
        "freq": "a",
        "label": "GDP_bln_rub",
        "date": '1999-12-31',
        "value": 4823,
    }


class BaseTest:    
    doc = ""
    
    def setup_method(self):
        self.f = Path("temp.txt").resolve()
        self.f.write_text(self.doc, encoding="utf-8")
        self.filename = str(self.f)

    def teardown_method(self):
        self.f.unlink()


class Test_to_values_on_namer_with_reader_parameter_and_doc(BaseTest):
    doc = """	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles
1999	653,8	22,7	49,2	91,5	138,7	185,0	240,0	288,5	345,5	400,6	454,0	528,0"""

    def test_to_values(self):
        namer = Namer(
            headers=["Консолидированные бюджеты субъектов"],
            name="VARX",
            units=["bln_rub"],
            reader="fiscal",
        )
        dps = reader.to_values(
            filename=self.filename,
            unit_mapper_dict=UNITS,
            namers=[namer]
        )
        assert dps[11] == {
            "freq": "m",
            "label": "VARX_bln_rub",
            "date": '1999-11-30',
            "value": 528.0,
        }
        assert dps[0] == {
            "freq": "a",
            "label": "VARX_bln_rub",
            "date": '1999-12-31',
            "value": 653.8,
        }

class Test_to_values_on_namer_with_startend_and_csv(object):    
    def test_returns_Expects_value_after_start(self):
        namer = Namer(
            name="EXPORT_GOODS",
            headers=["экспорт товаров – всего", "Экспорт товаров"],
            units=["bln_usd"],
            starts=[
                "1.9. Внешнеторговый оборот – всего",
                "1.10. Внешнеторговый оборот – всего",
                "1.10. Внешнеторговый оборот – всего",
            ],
            ends=[
                "1.9.1. Внешнеторговый оборот со странами дальнего зарубежья",
                "1.10.1. Внешнеторговый оборот со странами дальнего зарубежья",
                "1.10.1.Внешнеторговый оборот со странами дальнего зарубежья",
            ],
        )
        dps = reader.to_values(filename=PATH, unit_mapper_dict=UNITS, namers=[namer])
        assert dps[0]["value"] == 75.6
        # as in:
        # 1.9. Внешнеторговый оборот – всего1), млрд.долларов США / Foreign trade turnover – total1), bln US dollars
        # Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.
        #		I	II	III	IV
        # в том числе:
        # экспорт товаров – всего, млрд.долларов США
        # / of which: export of goods – total, bln US dollars
        # 1999	75,6	15,3	17,1	18,9	24,3	4,5	4,9	5,8	6,6	5,1	5,4	6,3	6,2	6,4	7,0	7,6	9,7
        #    # example 3
        #    # a) trailing tables eg find industrial production ytd from tables[4]

class Test_parsed_tables_on_trailing_tables(object):    
    def test_returns_tables_with_three_units(self):
        namer = Namer(
            name="INDPRO",
            headers=["Индекс промышленного производства"],
            units=["yoy", "rog", "ytd"],
        )
        tables = reader.parsed_tables(filename=PATH, unit_mapper_dict=UNITS, namers=[namer])

        assert [t.label for t in tables if t.is_defined()] == [
            "INDPRO_yoy",
            "INDPRO_rog",
            "INDPRO_ytd",
        ]
        datapoints = [x for x in reader.emit_datapoints(tables)]
        assert datapoints[148] == {
            "freq": "m",
            "label": "INDPRO_ytd",
            "date": '2018-04-30',
            "value": 101.8,  # checked at csv.txt
        }
        assert datapoints[0] == {
            "freq": "a",
            "label": "INDPRO_yoy",
            "date": '2015-12-31',
            "value": 99.2,  # checked at csv.txt
        }
            


def test_bugfix_short_unit_name():
    #   regression test 'млрд.тонно-км'
    assert (
        "млрд.тонно-км"
        in "1.5. Грузооборот транспорта, включая коммерческий и некоммерческий грузооборот, млрд.тонно-км / Freight turnover, including commercial and noncommercial freight turnover, bln ton-km"
    )
    text = "1.5. Грузооборот транспорта, включая коммерческий и некоммерческий грузооборот, млрд.тонно-км / Freight turnover, including commercial and noncommercial freight turnover, bln ton-km"
    row = [text, "", ""]
    t = reader.Table(headers=[row], datarows=[["100"] * 5])
    assert t.headers_contain("млрд.тонно-км")
    assert "млрд.тонно-км" in UNITS.keys()
    assert UNITS["млрд.тонно-км"] == "bln_tkm"
    tables = [t]
    reader.put_units(tables, UNITS)
    b = tables[0]
    assert b.unit == "bln_tkm"
