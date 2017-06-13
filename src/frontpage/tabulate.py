"""Formatting of output by column for markdown."""

# -----------------------------------------------------------------
# Functions:
#    pure_tabulate(iter, header=TABLE_HEADER)
#    printable(textlist, sep = " "):
# -----------------------------------------------------------------

NCOL = 2

def add_tail(lst, n = NCOL):
    """Add extra elements at end of lst"""
    extra_blanks = (len(lst) // n + 1) * n - len(lst)
    return lst + [' ' for x in range(extra_blanks)]

def chunks(lst, n = NCOL):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def get_max_width_in_list(textlist):
    return max([len(t) for t in textlist])

def cell_format(max_width):
    """

    :rtype: string
    """
    return "{:<" + str(max_width) + "}"
    
def printable(textlist, sep = " "):
    """Returns a string with elements of *testlist* printied by NCOL columns."""
    max_width = get_max_width_in_list(textlist)
    cell_pattern = cell_format(max_width)    
    return '\n'.join([sep.join([cell_pattern.format(x) for x in line]) for line in chunks(add_tail(textlist))])

#----------------------------------------------------------------------------------------------------------------
        
import itertools
TABLE_HEADER = ["Код", "Описание", "Ед.изм.", "Частота"]

def get_max_widths(table):
    """
    For a table with N columns, returns list of N integers,
    where each element is the maximum width of the corresponding column.

    Supports incomplete rows with less than N elements.
    
    *table* is a list of lists.
    """
    max_widths = []
    column_count = 0
    for row in table:
        #extend incomplete rows
        if len(row) > column_count:
            max_widths.extend([0 for _ in range(len(row) - column_count)])
            column_count = len(max_widths)
        # count widths
        for i, value in enumerate(row):
            max_widths[i] = max(max_widths[i], len(value))
    return max_widths


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

def add_dividers(row, divider="|", padding=0):
    """Add dividers and padding to a row of cells and return a string."""
    div = ''.join([padding * ' ', divider, padding * ' '])
    return '| {} |'.format(div.join(row))

def horiz_div(col_widths):
    row = ['-' * x for x in col_widths]
    return '|:{}-|'.format('-|:'.join(row))
    
def tabulate(table, header=TABLE_HEADER):
    table = pad_cells([header] + table)
    header = table[0]
    body = table[1:]
    
    col_widths = [len(cell) for cell in header]
    horiz = horiz_div(col_widths)

    header = add_dividers(header)
    body = [add_dividers(row) for row in body]

    table = [header, horiz]
    table.extend(body)
    return '\n'.join(table)

def pure_tabulate(table, header=TABLE_HEADER):
    """Returns markdown-formatted table as a string.
    
    TABLE_HEADER = ["Код", "Описание", "Ед.изм.", "Частота"]
    table = [['35462356', 'wrt', 'wergwetrgwegwetg'], ['qrgfwertgwqert', 'abc']]
    
    pure_tabulate(table, TABLE_HEADER) result should be like below
    
    | Код            | Описание | Ед.изм.          | Частота |
    |:---------------|:---------|:-----------------|:--------|
    | 35462356       | wrt      | wergwetrgwegwetg |         |
    | qrgfwertgwqert | abc      |                  |         |
    
    """

    
    col_widths = [len(cell) for cell in header]
    horiz = horiz_div(col_widths, header_div, divider, padding)

    header = add_dividers(header, divider, padding)
    body = [add_dividers(row, divider, padding) for row in body]

    table = [header, horiz]
    table.extend(body)
    table = [row.rstrip() for row in table]
    return '\n'.join(table)
    
    # Calculate column widths
    widths = get_max_widths(itertools.chain([header], table))
    # | Text      | Another text |
    template =              '| ' + ' | '.join(cell_format(x) for x in widths) + ' |'
    #                        |:------|:------------------------------------|
    header_separator_line = '|:' + '-|:'.join('-' * x for x in widths) + '-|'

    # Format and combine all rows into table
    # If table row has less elements than widths, new elements must be added to the row.
    # Otherwise template.format(*row) will fail due to the missing elements.
    rows = [template.format(*header), header_separator_line]
    column_count = len(widths)
    for row in table:
        if column_count > len(row):
            col = column_count - len(row)
            row += [''] * col
        fitted_row = template.format(*row)
        rows.extend([fitted_row])
    return '\n'.join(rows)

if __name__ == '__main__':
    
    header = 'abc'
    table = [['hh', 'ggg', 'q'], '456']
    
    assert header[2] == 'c'
    assert table[1][2] == '6'
    #assert (get_max_widths(table)) == [2, 3, 1]
    print(tabulate(table, header))
    
    textlist = [['35462356', 'wrt', 'wergwetrgwegwetg'], ['qrgfwertgwqert', 'abc', "zzz"]]
    print(tabulate(textlist, header))

    #textlist = ['35462356', 'wrt', 'wergwetrgwegwetg', 'qrgfwertgwqert', 'abc']
    #print(printable(textlist))
    #print(pure_tabulate(chunks(add_tail(textlist, n = 4), n = 4), header=TABLE_HEADER))
        