# -*- coding: utf-8 -*-

# Parts of code from
# https://github.com/mplewis/csvtomd/blob/master/csvtomd/csvtomd.py
# skipped column normalisation, assumes good number of columns


def pad_cells(table):
    """Pad each cell to the size of the largest cell in its column."""
    col_sizes = [max(map(len, col)) for col in zip(*table)]
    for row in table:
        # allow table to contain tuples
        #row = [x for x in row]
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
    """Divider line like |:---|:----|:--|"""
    row = ['-' * x for x in col_widths]
    return '|:{}-|'.format('-|:'.join(row))


def tabulate(table):
    """Use first row as header"""
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


def to_markdown(body, header=None):
    """Return markdown table as string."""
    if header:
        table = [header]
    else:
        table = []
    table.extend([row for row in body])
    return tabulate(table)


if __name__ == "__main__":
    # TODO: move to test_to_markdown.py
    table = ["a", "bbb", "c"], ["zz", "z", "c"]
    print(tabulate(table))
    table = ['kkk462356', 'wrt', "11", 'wergwetrgwegwetg'], \
            ['qrgfwertgwqert', 'abc', "22", "zzz"]
    print()
    print(tabulate(table))
    #TABLE_HEADER = ["Описание", "Код"]
    print()
    print(to_markdown(body=table, header=["a", "b", "c", "d"]))
