from pathlib import Path
import sys

# add the 'kep_dir' directory as one where we can import modules
#    see 'Notebooks are for exploration and communication' in 
#    http://drivendata.github.io/cookiecutter-data-science/

kep_dir = Path(__file__).parents[1] / "kep" 
access_dir =  Path(__file__).parents[1] / "access_data"              
sys.path.extend([path.__str__() for path in [kep_dir, access_dir]])

import cfg
from to_markdown import to_markdown
from access_data import get_dfs_from_local

# TABLE 1 - Sections with required varnames
md1 = to_markdown(body=cfg.yield_variable_descriptions_with_subheaders(), 
                  header=["Показатель", "Код"])
path = Path(__file__).parent / "sections.md"
path.write_text(md1)  
print(md1)


# TABLE 2 - latest values for all montly variables 
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py#L120-L153
# or local old/frontpage.py#L120-L153

dfa, dfq, dfm = get_dfs_from_local()

#generate with latest values from monthly dataframe
def stream_table_rows(dfm=dfm):
    dfm = dfm.drop(['year', 'month'], 1)
    for name in dfm.columns:
       value, date = get_last(dfm, name) 
       #FIXME: generate and add sparklines
       #img = insert_image_to_md(name)
       #FIXME: pad_cells(table) wont accept tuple, need make it more type-agnostc
       yield [name, value, date]#, img

def get_last(df, lab):
    s = df[lab]
    ix = ~s.isnull()
    last_value = s[ix][-1]
    last_date = s.index[ix][-1]
    return str(round(last_value,2)), last_date.strftime("%m.%Y")

md2 = to_markdown(body=stream_table_rows(), 
                  header=["Код", "Значение", "Дата"])
path = Path(__file__).parent / "latest.md"
path.write_text(md2)  
print(md2)


# TABLE 3
# TODO: generate TABLE 3 with a column of sparklines as in below 
# https://github.com/epogrebnyak/data-rosstat-kep/blob/47229a4e668dbaee31dfb6419f510abe13d0d9a3/frontpage.py
# or local old/frontpage.py

# TABLE 4
# NOT TODO: mix table 1 and table 3