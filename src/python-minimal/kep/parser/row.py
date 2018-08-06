from collections import namedtuple
import kep.parser.filters as filters

__all__ = ['Datapoint', 'get_row_format', 'emit_datapoints']

# FIXME: does not look great in documentation
Datapoint = namedtuple('Datapoint', 'label freq year month value')   


ROW_FORMAT_DICT = {len(x): x for x in [
    'YAQQQQMMMMMMMMMMMM',
    'YAQQQQ',
    'YAMMMMMMMMMMMM',
    'YMMMMMMMMMMMM',
    'YQQQQ',
    'XXXX',
    'XXX',
    'X'*11,
    'X'*15,
    'X'*12]}
    
def get_row_format(datarows: list):
    """Return a format string like 'YAQQQQ'
    """
    _coln = coln(datarows)
    try:
        return ROW_FORMAT_DICT[_coln] 
    except KeyError:
        raise ValueError('Cannot guess row format', 
                          _coln,
                          datarows)   


def coln(datarows):
    return max([len(row) for row in datarows])


def get_month(freq: str, period: int):
    if freq == 'a':
        return 12
    elif freq == 'q':
        return period * 3
    return period


def emit_datapoints(row, label, row_format):
    """Yield Datapoint instances from *row*. 
    
       Args:       
         -  row(list) - list of strings like ['1999', '100', '100', '100', '100']
         -  label(str) - variable identificator like 'CPI_rog'
         -  row_format(str) - format string like 'YAQQQQ'
    """    
    occurences = ''
    for value, letter in zip(row, row_format):
        occurences += letter
        if letter == 'Y':
            year = filters.clean_year(value)
        else:
            if filters.is_omission(value):
                continue                
            period = occurences.count(letter)
            freq = letter.lower()
            try:
                yield Datapoint(label=label, 
                                freq=freq,
                                year=year,
                                month=get_month(freq, period), 
                                value=filters.clean_value(value))
            except UnboundLocalError:
                raise ValueError((row, label))

# WONTFIX
# must fail on row
#['до/up to 2000,0', '2,6', '1,5', '1,0']
