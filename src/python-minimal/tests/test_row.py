import kep
from kep.row import Datapoint

row1 = ['2018',
        '',
        '101,9', '', '', '',
        '102,9', '101,5', '101,0', '101,3', '', '', '', '', '', '', '', '']

format1 = kep.row.get_format(len(row1))


def test_get_format():
    assert format1 == 'YAQQQQMMMMMMMMMMMM'


def test_emit_datapoints():
    gen1 = kep.row.emit_datapoints(row1, 'INDPRO_yoy', format1)
    pts = list(gen1)
    assert pts == [
        Datapoint(
            label='INDPRO_yoy',
            freq='q',
            date='2018-03-31',
            value=101.9),
        Datapoint(
            label='INDPRO_yoy',
            freq='m',
            date='2018-01-31',
            value=102.9),
        Datapoint(
            label='INDPRO_yoy',
            freq='m',
            date='2018-02-28',
            value=101.5),
        Datapoint(
            label='INDPRO_yoy',
            freq='m',
            date='2018-03-31',
            value=101.0),
        Datapoint(
            label='INDPRO_yoy',
            freq='m',
            date='2018-04-30',
            value=101.3)]
