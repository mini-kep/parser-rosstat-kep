from collections import namedtuple
import kep.filters as filters

Datapoint = namedtuple('Datapoint', 'label freq year month value')   


def get_month(freq: str, period: int):
    if freq == 'a':
        return 12
    elif freq == 'q':
        return period * 3
    return period


def emit_datapoints(row, label, row_format):
    """Yield Datapoint instances from *row*.    
    Args:
        row(list) - lsit of strings
        label(list) - variable identificator
        row_format(list) - format as 'YAQQQQ'
    """    
    occurences = ''
    for value, letter in zip(row, row_format):
        occurences += letter
        if letter == 'Y':
            year = value
        else:
            if filters.is_omission(value):
                continue                
            period = occurences.count(letter)
            freq = letter.lower()
            try:
                yield Datapoint(label=label, 
                                freq=freq,
                                year=filters.clean_year(year),
                                month=get_month(freq, period), 
                                value=filters.clean_value(value))
            except UnboundLocalError:
                raise ValueError((row, label))

# WONTFIX
# must fail on row
#['до/up to 2000,0', '2,6', '1,5', '1,0']
