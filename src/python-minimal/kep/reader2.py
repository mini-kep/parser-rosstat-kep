import io 
import csv
from enum import Enum, unique
import re

import kep.filters as filters
import kep.row as row_model
from kep.label import make_label
from kep.definition.units import UnitMapper, BASE_UNITS


# convert CSV to Table() instances

def read_csv(file):
    """Read csv file as list of lists / matrix"""
    with open(file, 'r', encoding='utf-8') as f:
        read_bytes_as_csv(f)
            
def read_bytes_as_csv(f):
    for row in csv.reader(f, delimiter='\t', lineterminator='\n'):
         yield row

def import_tables(file):
    """Wraps read_csv() and split_to_tables() into one call."""
    return list(split_to_tables(read_csv(file)))

def import_tables_from_string(text):
    """Wraps read_csv() and split_to_tables() into one call."""
    matrix = read_bytes_as_csv(io.StringIO(text)) 
    return list(split_to_tables(matrix))


@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2


def split_to_tables(csv_rows):
    """Yield Table() instances from *csv_rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in csv_rows:
        # is data row?
        if filters.is_year(row[0]):
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:
                # table ended, emit it
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.HEADERS
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class Table:
    def __init__(self, headers, datarows, name=None, unit=None):
        self._headers = headers
        self.headers = [x[0] for x in headers if x[0]]
        self.datarows = datarows
        self.name = name
        self.unit = unit
        self.row_format = row_model.get_format(row_length=self.coln)

    def __eq__(self, x):
        return repr(self) == repr(x)

    def __bool__(self):
        return (self.name is not None) and (self.unit is not None)

    @property
    def label(self):
        if self:
            return make_label(self.name, self.unit)
        return None

    @property
    def coln(self):
        return max([len(row) for row in self.datarows])

    def contains_any(self, strings):
        for header in self.headers:
            for s in strings:
                if re.search(r'\b{}'.format(s), header):
                    return s
        return None

    def assign_row_format(self, key):
        self.row_format = row_model.assign_format(key)

    def emit_datapoints(self):
        _label = self.label
        for row in self.datarows:
            for d in row_model.emit_datapoints(row, _label, self.row_format):
                yield d

    def __repr__(self):
        return ',\n      '.join([f'Table(name={repr(self.name)}',
                                 f'unit={repr(self.unit)}',
                                 f'row_format={repr(self.row_format)}',
                                 f'headers={self.headers}',
                                 f'datarows={self.datarows[0]}'
                                 ]
    )

def iterate(x):
    if isinstance(x, str):
        return [x]
    else:
        return x

class TextContainer:
    def __init__(self, text: str, base_units: dict):
        tables = import_tables_from_string(text)
        self.incoming_tables = list(tables)
        self.tables = [] 
        self.parsed_tables = []
        self.curname = None
        self.base_mapper = UnitMapper(base_units)
        
    def push(self):
        self.parsed_tables.extend([t for t in self.tables if t])
        
    def init(self):
        self.tables = self.incoming_tables 

    def start_with(self, start_strings):
        self.init()
        start_strings = iterate(start_strings) 
        for i, t in enumerate(self.tables):
            if t.contains_any(start_strings):
                break
        self.tables = self.tables[i:]
        return self    
        
    def end_with(self, end_strings):
        end_strings = iterate(end_strings) 
        we_are_in_segment = True
        for i, t in enumerate(self.tables):
            if t.contains_any(end_strings):
                we_are_in_segment = False
            if not we_are_in_segment:    
                break
        self.tables = self.tables[:i]
        return self
    
    def assign_units(self, unit):
        for t in self.tables:
            t.unit = unit
        return self
   
    def set_name(self, name):
        self.curname = name
        
    def attach_headers(self, headers):
        headers = iterate(headers) 
        for t in self.tables:
           if t.contains_any(headers):
                t.name = self.curname 
        return self        

    def set_units(self, units):
        self.units = iterate(units)

    def parse_units(self):
        for i, t in enumerate(self.tables):
            for header in t.headers:
                unit = self.base_mapper.extract(header)
                if unit:
                    #self.tables[i].unit = unit
                    t.unit = unit

    def trail_down_units(self):
        pass

    def trail_down_names(self):
        pass

    def parse_units_with(self, mapper: dict={}):
        for t in self.tables:
            pass
        return self
    
    def require(self, string):
        label, freq, date, value = string.split(' ')
        value = float(value)
        assert row_model.Datapoint(label, freq, date, value) in self.datapoints
    
    @property
    def datapoints(self):
        return list(self.emit_datapoints())
    
    def emit_datapoints(self):
        for t in self.parsed_tables:
            if t:
                for x in t.emit_datapoints():
                    yield x

    @property
    def labels(self):
        return [t.label for t in self.tables] 

#TODO:
#    def prev_next_pairs(self):
#        return zip(self.tables[:-1], self.tables[1:]) 
#    
#    
#    def put_trailing_names(self, parser):
#        """Assign trailing variable names in tables.
#           Trailing names are defined in leading table and pushed down
#           to following tables, if their unit is specified in namers.units
#        """
#        _units = copy(parser.units)
#        for prev_table, table in self.prev_next_pairs():
#            if not _units:
#                break
#            if prev_table.name == parser.name:
#               try:
#                    _units.remove(prev_table.unit)
#               except ValueError:
#                    pass                    
#            if (table.name is None
#                and prev_table.name is not None
#                and table.unit in _units):
#                table.name = prev_table.name
#                print(table.headers)
#                print(_units)
#                _units.remove(table.unit)
#
#
#    def put_trailing_units(self, parser):
#        """Assign trailing variable names in tables.
#           Trailing names are defined in leading table and pushed down
#           to following tables, if their unit is specified in namers.units
#        """
#        for prev_table, table in self.prev_next_pairs():
#            if (table.unit is None
#                and prev_table.unit is not None
#                and table.name):
#                table.unit = prev_table.unit


def dict_key(d: dict):
    return list(d.keys())[0]


def apply(container, command):         
    if isinstance(command, str):
        func = getattr(container, command)
        func()
    elif isinstance(command, dict):
        method = dict_key(command)
        arg = command[method]
        func = getattr(container, method) 
        if isinstance(arg, dict):
            func(**arg)
        else:
            func(arg)
    return container        


# Fails on empty row 
#    if filters.is_year(row[0]):
# IndexError: list index out of range

CPI_TEXT = """	Год / Year	Кварталы / Quarters	Янв. Jan.	Фев. Feb.	Март Mar.	Апр. Apr.	Май May	Июнь June	Июль July	Август Aug.	Сент. Sept.	Окт. Oct.	Нояб. Nov.	Дек. Dec.			
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

doc = """
- init
- set_name: INDPRO
- attach_headers: Индекс промышленного производства
- set_units: 
    - yoy
    - rog
    - ytd
- parse_units
# TODO: traildown units    
- push
- require: INDPRO_yoy m 2015-12-31 98.1

- init
- start_with: '3.5. Индекс потребительских цен'
- end_with: '4. Социальная сфера'
- assign_units: rog
- set_name: CPI_NONFOOD
- attach_headers: 
  - 'непродовольственные товары'
  - 'непродовольст- венные товары'
- push
- require: CPI_NONFOOD_rog m 1999-12-31 101.1

- init
# TODO: change format to 'fiscal'
- start_with: '2.2. Сальдированный финансовый результат'
- end_with: 'Убыточные организации'
- assign_units: 'mln_rub'
- set_name: PROFIT_MINING
- attach_headers: Добыча полезных ископаемых
- push
"""   
if __name__ == '__main__':

    assert 'bln_rub' == UnitMapper(BASE_UNITS).extract('abc - млрд.рублей')   
    x = ("в % к соответствующему периоду предыдущего года "
         "/ percent of corresponding period of previous year")
    assert 'yoy' == UnitMapper(BASE_UNITS).extract(x)

    import yaml
    instr = yaml.load(doc)
    container = TextContainer(CPI_TEXT, BASE_UNITS)
    for command in instr:
        apply(container, command)
    assert container.parsed_tables
    assert container.parsed_tables[0]    

#TODO: read paths 
#def make(csv_path: str, 
#          instruction_path: str, 
#          default_units_path: str = None):
