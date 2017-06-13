# -*- coding: utf-8 -*-
from collections import OrderedDict as odict
from pathlib import Path  
# Parts of code form https://github.com/mplewis/csvtomd/blob/master/csvtomd/csvtomd.py

def pad_cells(table):
    """Pad each cell to the size of the largest cell in its column."""
    col_sizes = [max(map(len, col)) for col in zip(*table)]
    for row in table:
        for cell_num, cell in enumerate(row):
            row[cell_num] = pad_to(cell, col_sizes[cell_num])
    return table

def pad_to(unpadded, target_len):
    """
    Pad a string to the target length in characters, or return the original
    string if it's longer than the target length.
    """
    under = target_len - len(unpadded)
    if under <= 0:
        return unpadded
    return unpadded + (' ' * under)

def add_dividers(row):
    """Add dividers and padding to a row of cells and return a string."""
    div = " | "
    return '| {} |'.format(div.join(row))

def horiz_div(col_widths):
    row = ['-' * x for x in col_widths]
    return '|:{}-|'.format('-|:'.join(row))

def tabulate(table):
    table = pad_cells(table)
    header = table[0]
    body = table[1:]
    
    col_widths = [len(cell) for cell in header]
    header = add_dividers(header)
    horiz = horiz_div(col_widths)
    body = [add_dividers(row) for row in body]

    table = [header, horiz]
    table.extend(body)
    return '\n'.join(table)

def to_markdown(body, header):
    table = [header] + [row for row in body]
    return tabulate(table)

class Descriptions():

    header = ["Показатель", "Код"]
    
    def __init__(self, sections = ["ВВП и производство",
                         "Внешняя торговля",
                         "Розничная торговля"]):
        self.desc = odict()
        self.add("ВВП и производство",        
            ["Валовой внутренний продукт", "GDP"],
            ["Промышленное производство", "IND_PROD"])
        self.add("Внешняя торговля",        
            ["Экспорт товаров - всего", "EXPORT_GOODS_TOTAL"],
            ["Импорт товаров - всего", "IMPORT_GOODS_TOTAL"])       
        self.add("Розничная торговля", 
            ["Оборот розничной торговли - всего", "RETAIL_SALES"],
            ["Оборот розничной торговли - продовольственные товары", "RETAIL_SALES_FOOD"],
            ["Оборот розничной торговли - непродовольственные товары", "RETAIL_SALES_NONFOODS"])
        
    def add(self, section, *args):
        desc_and_lables = [[arg[0], arg[1]] for arg in args]
        self.desc.update([(section, desc_and_lables)])

    def as_markdown(self):
        table = []
        for k,v in self.desc.items(): 
            table_segment = ([["**{}**".format(k), ""]] + v)
            table.extend(table_segment)
        return to_markdown(table, self.header)
    
    def to_file(self, file="frontpage1.md")     :
        path = Path(__file__).parent / file
        path.write_text(self.as_markdown())           
            

if __name__ == "__main__":
    # move to tests
    #table = [["a", "bbb", "c"], ["zz", "z", "c"]]    
    #print(tabulate(table))
    #table = ['35462356', 'wrt', "a", 'wergwetrgwegwetg'], ['qrgfwertgwqert', 'abc', "22", "zzz"]
    #print(tabulate(table))
    #TABLE_HEADER = ["Код", "Описание", "Ед.изм.", "Частота"]
    #print()
    #print(to_markdown(table, TABLE_HEADER))    
    #tabulate ([('Валовой внутренний продукт', 'GDP'), ('Промышленное производство', 'IND_PROD')])   
    print(Descriptions().as_markdown())
    Descriptions().to_file()
    
    # TODO:
    # Accum
    # read latest values
    # latest values
    # rog/yoy  - see required variables  