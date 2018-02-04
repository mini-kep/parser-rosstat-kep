"""Parse CSV text *csv_segment* using parsing definition *pdef*:

   extract_tables(csv_segment, pdef)

"""

from collections import OrderedDict as odict
from enum import Enum, unique

import kep.csv2df.util.row_splitter as splitter
from kep.csv2df.row_model import Row
from kep.csv2df.row_stack import text_to_list
from kep.csv2df.util.label import make_label
from kep.csv2df.util.to_float import to_float

__all__ = ['extract_tables']


def extract_tables(csv_segment: str, pdef):
    """Extract tables from *csv_segment* string using *pdef* parsing defintion.

    Args:
        csv_segment(str): CSV text
        pdef: parsing defintion with search strings for header and unit

    Returns:
        list of Table() instances    
    """
    tables = split_to_tables(csv_segment)
    tables = parse_tables(tables, pdef)
    verify_tables(tables, pdef)
    return [t for t in tables if t.label in pdef.required]


def parse_tables(tables, pdef):
    # assign reader function
    tables = [t.set_splitter(pdef.reader) for t in tables]
    # parse tables to obtain labels - set label and splitter
    tables = [t.set_label(pdef.mapper, pdef.units) for t in tables]
    # assign trailing units

    def fix_multitable_units(tables):
        """For tables without *varname* - copy *varname* from previous table.
           Applies to tables where all rows are known rows.
        """
        for prev_table, table in zip(tables, tables[1:]):
            if table.varname is None and not table.has_unknown_lines():
                table.varname = prev_table.varname
    fix_multitable_units(tables)
    return tables


def verify_tables(tables, pdef):
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in pdef.required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels: {}".format(labels_missed))


@unique
class RowType(Enum):
    UNKNOWN = 0
    DATA = 1
    SECTION = 2
    HEADER = 3


@unique
class State(Enum):
    INIT = 1
    DATA = 2
    UNKNOWN = 3


def split_to_tables(rows):
    """Yields Table() instances from *rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        r = Row(row)
        if r.is_datarow():
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:  # table ended
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.UNKNOWN
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class Table:
    """Representation of CSV table, has headers and datarows."""

    KNOWN = "+"
    UNKNOWN = "-"

    def __init__(self, headers, datarows):
        self.headers = headers
        self.datarows = datarows
        # parsing
        self.splitter_func = None
        self.varname = None
        self.unit = None
        self.datapoints = []
        # header indicator
        self.lines = odict((Row(row).name, self.UNKNOWN) for row in headers)

    @property
    def coln(self):
        """Number of columns in table."""
        return max(len(Row(row)) for row in self.datarows)

    def set_label(self, varnames_dict, units_dict):
        for row in self.headers:
            r = Row(row)
            varname = r.get_varname(varnames_dict)
            if varname:
                self.varname = varname
                self.lines[Row(row).name] = self.KNOWN
            unit = r.get_unit(units_dict)
            if unit:
                self.unit = unit
                self.lines[Row(row).name] = self.KNOWN
        return self

    def set_splitter(self, reader):
        self.splitter_func = splitter.get_splitter(reader or self.coln)
        return self

    @property
    def label(self):
        vn = self.varname
        u = self.unit
        if vn and u:
            return make_label(vn, u)
        else:
            return None

    def is_defined(self):
        return bool(self.label and self.splitter_func)

    def has_unknown_lines(self):
        return self.UNKNOWN in self.lines.values()

    def __eq__(self, x):
        return self.headers == x.headers and self.datarows == x.datarows

    def __str__(self):
        show = ["Table {} ({} columns)".format(self.label, self.coln),
                '\n'.join(["{} <{}>".format(v, k)
                           for k, v in self.lines.items()]),
                '\n'.join([str(row) for row in self.datarows])
               ]
        return "\n".join(show)

    def __repr__(self):
        return "Table(\n    headers={},\n    datarows={})" \
               .format(repr(self.headers), repr(self.datarows))

    def make_datapoint(self, value: str, time_stamp, freq):
        return dict(label=self.label,
                    value=to_float(value),
                    time_index=time_stamp,
                    freq=freq)

    def extract_values(self):
        """Yield dictionaries with variable name, frequency, time_index 
           and value.
        """
        for row in self.datarows:
            year = Row(row).year
            data = Row(row).data
            a_value, q_values, m_values = self.splitter_func(data)
            if a_value:
                time_stamp = timestamp_annual(year)
                yield self.make_datapoint(a_value, time_stamp, 'a')
            if q_values:
                for t, val in enumerate(q_values):
                    time_stamp = timestamp_quarter(year,  t + 1)
                    yield self.make_datapoint(val, time_stamp, 'q')
            if m_values:
                for t, val in enumerate(m_values):
                    time_stamp = timestamp_month(year,  t + 1)
                    yield self.make_datapoint(val, time_stamp, 'm')


import pandas as pd


def timestamp_annual(year):
    return pd.Timestamp(year, 12, 31)


def timestamp_quarter(year, quarter):
    month = quarter * 3
    return timestamp_month(year, month)


def timestamp_month(year, month):
    return pd.Timestamp(year, month, 1) + pd.offsets.MonthEnd()


if __name__ == "__main__":  # pragma: no cover
    DOC = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""
    rows = text_to_list(DOC)
    tables = list(split_to_tables(rows))
    t = tables[0]
    t.set_splitter(None)
    t.varname = 'GDP'
    t.unit = 'bln_rub'
    datapoints = list(t.extract_values())
    assert datapoints[0] == {'freq': 'a',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-12-31'),
                             'value': 4823}
    assert datapoints[1] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-03-31'),
                             'value': 901}
    assert datapoints[2] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-06-30'),
                             'value': 1102}
    assert datapoints[3] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-09-30'),
                             'value': 1373}
    assert datapoints[4] == {'freq': 'q',
                             'label': 'GDP_bln_rub',
                             'time_index': pd.Timestamp('1999-12-31'),
                             'value': 1447}
#    [['1. Сводные показатели / Aggregated indicators', '', '', '', '', ''],
# ['1.1. Валовой внутренний продукт1) / Gross domestic product1)',
#  '',
#  '',
#  '',
#  '',
#  ''],
# ['1.1.1. Объем ВВП, млрд.рублей /GDP, bln rubles', '', '', '', '', ''],
# ['1999', '4823', '901', '1102', '1373', '1447'],
# ['2000', '7306', '1527', '1697', '2038', '2044'],
# ['2001', '8944', '1901', '2105', '2488', '2450'],
# ['2002', '10831', '2262', '2529', '3013', '3027'],]
    
