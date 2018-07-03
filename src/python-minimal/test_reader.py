import reader


def test_emit_datapoints_from_row_on_YAQQQ():
    row1 = ['1999', '4823', '901', '1102', '1373', '1447']
    dps1 = list(reader.emit_datapoints_from_row(row=row1,
                                                label='GDP_bln_rub',
                                                row_format='YAQQQQ'))
    assert dps1 == [dict(label='GDP_bln_rub', freq='a', year='1999', period=1, value='4823'),
                    dict(label='GDP_bln_rub', freq='q', year='1999', period=1, value='901'),
                    dict(label='GDP_bln_rub', freq='q', year='1999', period=2, value='1102'),
                    dict(label='GDP_bln_rub', freq='q', year='1999', period=3, value='1373'),
                    dict(label='GDP_bln_rub', freq='q', year='1999', period=4, value='1447'),
                    ]


def test_emit_datapoints_from_row_on_YA12M():
    row2 = [
        '2015',
        '94,6',
        '91,4',
        '110,9',
        '96,2',
        '102,7',
        '98,0',
        '103,4',
        '100,9',
        '99,1',
        '103,9',
        '95,9',
        '104,2']
    dps2 = list(reader.emit_datapoints_from_row(row=row2,
                                                label='MINING_rog',
                                                row_format='YMMMMMMMMMMMM'))
    assert dps2[0] == {
        'freq': 'm',
        'label': 'MINING_rog',
        'period': 1,
        'value': '94,6',
        'year': '2015'}
    assert dps2[11] == {
        'freq': 'm',
        'label': 'MINING_rog',
        'period': 12,
        'value': '104,2',
        'year': '2015'}
