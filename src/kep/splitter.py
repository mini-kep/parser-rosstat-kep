"""Splitter functions extract annual, quarterly and monthly values from data row."""


def split_row_by_periods(row):
    """Values format:
       A Q Q Q Q M*12

    >>> split_row_by_periods(['2015','a','b','c','d',1,2,3,4,5,6,7,8,9,10,11,12])
    ('2015', ['a', 'b', 'c', 'd'], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])"""

    return row[0], row[1:1 + 4], row[1 + 4:1 + 4 + 12]


def split_row_by_year_and_qtr(row):
    """Values format:
       A Q Q Q Q

    >>> split_row_by_year_and_qtr(['85881', '18561', '19979', '22190', ''])
    ('85881', ['18561', '19979', '22190', ''], None)"""

    return row[0], row[1:1 + 4], None


def split_row_by_months(row):
    """Values format:
       M*12

    >>> split_row_by_months([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    (None, None, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    >>> split_row_by_months(['1697', '1832', '2317', '3066', '3607', '4111', '3856', '3530', '2961', '2149', '1565', '1583'])
    (None, None, ['1697', '1832', '2317', '3066', '3607', '4111', '3856', '3530', '2961', '2149', '1565', '1583'])"""

    return None, None, row[0:12]


def split_row_by_months_and_annual(row):
    """Values format:
       A M*12

    >>> split_row_by_months_and_annual([78] + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    (78, None, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    >>> 78 == sum([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    True


    >>> split_row_by_months_and_annual(['32259', '1703', '1853', '2305', '3049', '3590', '4007', '3891', '3515', '2917', '2160', '1613', '1656'])
    ('32259', None, ['1703', '1853', '2305', '3049', '3590', '4007', '3891', '3515', '2917', '2160', '1613', '1656'])
    >>> 32259 == sum(int(x) for x in            ['1703', '1853', '2305', '3049', '3590', '4007', '3891', '3515', '2917', '2160', '1613', '1656'])
    True
    """

    return row[0], None, row[1:12 + 1]


def split_row_by_accum_qtrs(row):
    """Values format:
       Annual AccumQ1 AccumH1 Accum9mo
       <I квартал Q 1>	<I полугодие 1st half-year>	<Январь-сентябрь January-September>

    >>> split_row_by_accum_qtrs (['35217','6372','7236','33523'])
    ('35217', ['6372', '7236', '33523', '35217'], None)"""

    return row[0], row[1:1 + 3] + [row[0]], None


def emit_nones(row):
    print("WARNING: unexpected number of columns {}".format(len(row)))
    print(row)
    return [None] * len(row)


#	Год Year	Янв. Jan.	Янв-фев. Jan-Feb	I квартал Q1	Янв-апр. Jan-Apr	Янв-май Jan-May	I полугод. 1st half year	Янв-июль Jan-Jul	Янв-авг. Jan-Aug	Янв-cент. Jan-Sent	Янв-окт. Jan-Oct	Янв-нояб. Jan-Nov
# Консолидированные бюджеты субъектов Российской Федерации, млрд.рублей / Consolidated budgets of constituent entities of the Russian Federation, bln rubles
# 1999	653,8	22,7	49,2	91,5	138,7	185,0	240,0	288,5	345,5	400,6	454,0	528,0
#   0	    1	   2      3 	   4	    5	    6	    7	    8	    9	   10	   11	   12
#          0     1      2     3       4      5      6      7     8      9     10     11


def split_row_fiscal(row):
    """
    >>> split_row_fiscal(['653,8', '22,7', '49,2', '91,5', '138,7', '185,0', '240,0', '288,5', '345,5', '400,6', '454,0', '528,0'])
    ('653,8', ['91,5', '240,0', '400,6', '653,8'], ['22,7', '49,2', '91,5', '138,7', '185,0', '240,0', '288,5', '345,5', '400,6', '454,0', '528,0', '653,8'])

    TODO: summ up differences by months, must be equal to 653,8
    accum_by_month_str = ['22,7', '49,2', '91,5', '138,7', '185,0', '240,0', '288,5', '345,5', '400,6', '454,0', '528,0', '653,8']
    """
    return row[0], [row[x] for x in [3, 6, 9, 0]], row[1:1 + 12] + [row[0]]


FUNC_MAPPER = {1 + 4 + 12: split_row_by_periods,
               1 + 4: split_row_by_year_and_qtr,
               1 + 12: split_row_by_months_and_annual,
               12: split_row_by_months,
               4: split_row_by_accum_qtrs,
               'fiscal': split_row_fiscal}


def get_splitter(arg):
    try:
        return FUNC_MAPPER[arg]
    except KeyError:
        return emit_nones


if __name__ == "__main__":
    pass
