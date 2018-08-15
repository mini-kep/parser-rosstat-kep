from kep.engine.row import Datapoint, emit_datapoints

row1 = ['2018',
        '100',
        '101,9', '', '', '',
        '102,9', '101,5', '', '', '', '', '', '', '', '', '', '']


def test_emit_datapoints():
    gen1 = emit_datapoints(row1, 'INDPRO_yoy', 'YAQQQQMMMMMMMMMMMM')
    pts = list(gen1)
    assert pts == [
        Datapoint(
            label='INDPRO_yoy',
            freq='a',
            year=2018,
            month=12,
            value=100),
        Datapoint(
            label='INDPRO_yoy',
            freq='q',
            year=2018,
            month=3,
            value=101.9),
        Datapoint(
            label='INDPRO_yoy',
            freq='m',
            year=2018,
            month=1,
            value=102.9),
        Datapoint(
            label='INDPRO_yoy',
            freq='m',
            year=2018,
            month=2,
            value=101.5),
    ]
