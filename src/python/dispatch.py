"""Parse CSV text *csv_segment* using parsing definition *pdef*:

   evaluate(rows, pdef)
"""
from enum import Enum, unique
import re

import pandas as pd

from util.csv_reader import read_csv
from extract.to_float import to_float
from extract.row_splitter import get_splitter
from util.csv_reader import pop_rows
from inputs.instruction import InstructionSet


@unique
class State(Enum):
    INIT = 0
    DATA = 1
    HEADERS = 2


YEAR_CATCHER = re.compile("\D*(\d{4}).*")


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from *string* using *rx* regex.

       Returns:
           Year as integer
           False if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991 and year <= 2050:
            return year
    return False


def is_year(string: str) -> bool:
    return get_year(string) is not False


def split_to_tables(rows):
    """Yield Tab() instances from *rows* list of lists."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        # is data row?
        if is_year(row[0]):
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
    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows
        self.name = None
        self.unit = None
        key = self.count_columns(self.datarows)
        self.set_reader(key)

    def set_reader(self, reader=None):
        if reader:
            self.splitter_func = get_splitter(reader)

    @property
    def label(self):
        if self.name and self.unit:
            return self.name, self.unit
        return None

    @property
    def heads(self):
        return [x[0] for x in self.headers]

    @staticmethod
    def count_columns(datarows):
        """Number of columns in table."""
        return max([len(row[1:]) for row in datarows])

    def make_datapoint(self, value: str, time_stamp, freq):
        return dict(label=(self.name, self.unit),
                    value=to_float(value),
                    time_index=time_stamp,
                    freq=freq)

    def yield_values(self):
        """Yield dictionaries with variable name, frequency, time_index
           and value. May yield a dictionary where d['value'] is None.
        """
        for row in self.datarows:
            year = get_year(row[0])
            data = row[1:]
            a_value, q_values, m_values = self.splitter_func(data)
            if a_value:
                time_stamp = timestamp_annual(year)
                yield self.make_datapoint(a_value, time_stamp, 'a')
            if q_values:
                for t, val in enumerate(q_values):
                    time_stamp = timestamp_quarter(year, t + 1)
                    yield self.make_datapoint(val, time_stamp, 'q')
            if m_values:
                for t, val in enumerate(m_values):
                    time_stamp = timestamp_month(year, t + 1)
                    yield self.make_datapoint(val, time_stamp, 'm')

    def __repr__(self):
        return str(self.__dict__)


def timestamp_annual(year):
    return pd.Timestamp(year, 12, 31)


def timestamp_quarter(year, quarter):
    month = quarter * 3
    return timestamp_month(year, month)  # .date()


def timestamp_month(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()


def assign_trailing_units(tables, required):
    tables = list(tables)
    for prev_table, table in zip(tables, tables[1:]):
        required_units = required.get(prev_table.name, [])
        if (table.name is None
                and table.unit in required_units):
            table.name = prev_table.name
        if (table.unit is None
                and table.name is not None):
            table.unit = prev_table.unit


def yield_values(tables):
    for t in tables:
        if t.name and t.unit:
            for x in t.yield_values():
                yield x


def var_parser(headers, name):
    def _enclosed(table):
        for pat in headers:
            regex = re.compile(r"\b{}".format(pat))
            for x in table.heads:
                if bool(re.search(regex, x)):
                    table.name = name
        return table
    return _enclosed


def unit_parser(units_ordered_dict):
    def _enclosed(table):
        for text, unit in units_ordered_dict.items():
            for row in table.heads:
                if text in row:
                    table.unit = unit
                    return table
        return table
    return _enclosed


def includes_required(tables, required):
    req = [(name, unit) for name, units in required.items() for unit in units]
    labs = [t.label for t in tables if t.label]
    diff = set(req) - set(labs)
    return diff == set()


def _render(csv_rows, unit_dict, headers_dict, required, reader):
    tables = split_to_tables(csv_rows)
    vparsers = [var_parser(headers, name)
                for name, headers in headers_dict.items()]
    uparser = unit_parser(unit_dict)
    for parser in vparsers + [uparser]:
        tables = map(parser, tables)
    tables = list(tables)
    assign_trailing_units(tables, required)
    if reader:
        for t in tables:
            t.set_reader(reader)
    return tables


def render(csv_rows, unit_dict, headers_dict, required, reader):
    tables = _render(csv_rows, unit_dict, headers_dict, required, reader)
    try:
        req = [(name, unit) for name, units in required.items()
               for unit in units]
        labs = [t.label for t in tables if t.label]
        diff = set(req) - set(labs)
        assert diff == set()
    except AssertionError:
        raise AssertionError(dict(diff=diff,
                                  headers_dict=headers_dict,
                                  tables=[(t.name, t.unit) for t in tables]
                                  ))
    return tables


def split_to_segments(csv_text: str, yaml_doc):
    csv_rows = read_csv(csv_text)
    segment_definitions = InstructionSet(yaml_doc).by_segment
    for pdef in segment_definitions:
        start, end = pdef.select_applicable_boundaries(csv_rows)
        csv_segment = pop_rows(csv_rows, start, end)
        yield csv_segment, pdef
    yield csv_rows, InstructionSet(yaml_doc).default


def evaluate(csv_text: str, units: dict, yaml_doc: str):
    for csv_rows, pdef in split_to_segments(csv_text, yaml_doc):
        tables = render(csv_rows,
                        units,
                        pdef.headers_dict,
                        pdef.required,
                        pdef.reader)
        for value in yield_values(tables):
            yield value


if __name__ == "__main__":  # pragma: no cover

    doc = """2.2. Сальдированный финансовый результат1) по видам экономической деятельности, млн.рублей / Balanced financial result by economic activity, mln rubles
Добыча полезных ископаемых / Mining and quarrying
2017	2595632	258752	431071	582484	786597	966414	1288872	1488124	1676187	1890266	2124278	2384759
2018		340136	502726	840956
Обрабатывающие производства / Manufacturing
2017	2902753	109158	328302	603088	879688	1055179	1339108	1510626	1788974	2122127	2457117	2703476
2018		201347	368925	634681
Обеспечение электрической энергией, газом и паром; кондиционирование воздуха / Electricity, gas, steam and air conditioning supply
2017	560093	94490	197250	241468	298346	380620	367380	401597	428841	415145	481313	567104
2018		94582	207510	274096
Строительство / Construction
2017	135639	7878	8182	-9556	5922	33368	17945	39012	58646	27260	46791	87103
2018		12601	17696	421
Транспортировка и хранение / Transport and storage
2017	910754	100190	172362	224896	300570	374104	454247	591818	708210	789956	906612	981043
2018		106770	160292	109203
	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
Убыточные организации"""

    # test 2
    csv_rows = read_csv(doc)
    tables = render(
        csv_rows,
        unit_dict={
            'млн.рублей': 'mln_rub'},
        headers_dict={
            'PROFIT_MINING': ['Добыча полезных ископаемых'],
            'PROFIT_MANUF': ['Обрабатывающие производства']},
        required={
            'PROFIT_MINING': ['mln_rub']},
        reader=None)
    values = list(yield_values(tables))


#    # test 4
#    from manage import Locations
#    from inputs import UNITS, YAML_DOC, verify
#    from util.dataframe import create_dataframe
#
#    pdef = InstructionSet(YAML_DOC).default
#    loc = Locations(2010, 1)
#    csv_text = loc.interim_csv.read_text(encoding='utf-8')
#    _tables = _render(read_csv(csv_text),
#                     UNITS,
#                     pdef.headers_dict,
#                     pdef.required,
#                     pdef.reader)
#    values = list(evaluate(csv_text, UNITS, YAML_DOC))
#    dfs = {}
#    for freq in 'aqm':
#        df = create_dataframe(values, freq)
#        dfs[freq] = df
#        verify(df, freq)
