# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 12:46:51 2017

@author: PogrebnyakEV
"""
from pathlib import Path
import sys
from itertools import chain
import itertools
import pandas as pd

# see 'Notebooks are for exploration and communication' in
# http://drivendata.github.io/cookiecutter-data-science/


def get_root():
    return Path(__file__).parents[2]


src_root = Path(__file__).parents[1]
sys.path.extend([str(src_root / "kep"), str(src_root / "access_data")])


import cfg
from to_markdown import to_markdown
import access_data
import sparkline


def get_last(df, lab):
    if lab in df.columns:
        s = df[lab]
        ix = ~s.isnull()
        last_value = s[ix][-1]
        last_date = s.index[ix][-1]
        return str(round(last_value, 2)), last_date  # .strftime("%m.%Y")
    else:
        return "", pd.Timestamp("1900")


def extract_varname(label):
    words = label.split('_')
    return '_'.join(itertools.takewhile(lambda word: word.isupper(), words))


def bold(s):
    return"**{}**".format(s)


dfa, dfq, dfm = access_data.get_dfs()

LABELS = list(set(chain.from_iterable(df.columns for df in [dfa, dfq, dfm])))
VARNAMES = {lab: extract_varname(lab) for lab in LABELS}
GROUPS = {}
for vn in set(VARNAMES.values()):
    common = []
    for lab in LABELS:
        if extract_varname(lab) == vn:
            common.append(lab)
    GROUPS[vn] = common


def get_unit_name(label, units=cfg.UNIT_NAMES):
    for key in units.keys():
        if label.endswith(key):
            return units[key]


def d1(sections=cfg.SECTIONS, desc=cfg.DESC):
    for section_name, varnames in sections.items():
        yield [bold(section_name), ""]
        for vn in varnames:
            if len(GROUPS[vn]) > 1:
                yield [desc[vn], ""]
                for lab in GROUPS[vn]:
                    unit_name = " - {}".format(get_unit_name(lab))
                    yield [unit_name, lab]
            else:
                lab = GROUPS[vn][0]
                text = "{}, {}".format(desc[vn], get_unit_name(lab))
                yield [text, lab]


def get_desc(label):
    vn = extract_varname(label)
    return cfg.DESC[vn]


def e1(sections=cfg.M_SECTIONS, desc=cfg.DESC):
    for section_name, labels in sections.items():
        yield dict(desc=bold(section_name), lab=None, unit=None)
        for lab in labels:
            yield dict(desc=get_desc(lab), unit=get_unit_name(lab), lab=lab)


def e2(f=e1):
    for x in f():
        d = {}
        d["m"], dt = get_last(dfm, x['lab'])
        d['date'] = dt.strftime("%m.%Y")
        yield {**x, **d}


def e3(f=e2):
    for x in f():
        if x['lab']:
            md = sparkline.Namer(x['lab']).markdown()
        else:
            md = ""
        yield {**x, "img": md}


def e4(f=e3):
    header = ["Показатель", "Ед.изм.", "График", "Значение", "Дата"]
    yield header
    prev_desc = ""
    for x in f():
        if x['lab']:
            if x['desc'] == prev_desc:
                desc = ""
            else:
                desc = x['desc']
            yield [desc, x['unit'], x['img'], x['m'], x['date']]
        else:
            t = ["" for _ in header]
            t[0] = x['desc']
            yield t
        prev_desc = x['desc']


def te():
    table = []
    table.extend([row for row in e4()])
    return "\n\n### Месячные значения\n\n" + to_markdown(table)


def latest(lab, m=dfm, q=dfq, a=dfa):
    d = {}
    d["m"], dt1 = get_last(m, lab)
    d["q"], dt2 = get_last(q, lab)
    d["a"], dt3 = get_last(a, lab)
    d["date"] = max([dt1, dt2, dt3]).strftime("%m.%Y")
    return d


def d2():
    for x in d1():
        lab = x[1]
        if lab:
            d = latest(lab)
            z = x + [d['date']] + [d[key] for key in 'aqm']
        else:
            z = x + [""] * 4
        yield z


def d3():
    for x in d2():
        lab = x[1]
        if x[-1]:
            md = sparkline.Namer(lab).markdown()
            x.append(md)
        else:
            x.append("")
        yield x


def d4():
    for x in d3():
        yield [x[z] for z in [0, 2, 5, 6]]


t1 = to_markdown(d4(), header=["Показатель",  # 0
                               # "Обозначение", #1
                               "Дата",  # 2
                               #"Год", #3
                               #"Квартал", #4
                               "Месяц",  # 5
                               "График (мес.)"  # 6
                               ])
if __name__ == "__main__":
    print(te())

    # print(list(d3()))
    # print(t1)


# TODO: add Excel file
# TODO: automate new
