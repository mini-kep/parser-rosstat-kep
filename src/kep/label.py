"""Variable labels.

Used to handle names like GDP_rog, GOV_EXPENSE_bln_rub.

"""

__all__ = [
    'make_label',
    'split_label',
    'extract_varname',
    'extract_unit'
]


import itertools


SEP = '_'


def make_label(vn, unit, sep=SEP):
    return vn + sep + unit


def split_label(label):
    return extract_varname(label), extract_unit(label)


def extract_varname(label):
    words = label.split('_')
    return SEP.join(itertools.takewhile(lambda word: word.isupper(), words))


def extract_unit(label):
    words = label.split('_')
    return SEP.join(itertools.dropwhile(lambda word: word.isupper(), words))
