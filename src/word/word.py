"""make_csv(data_folder) dumps data from tables in Word document to csv file.
   Windows-only, requires MS Word installed.
"""

# More info on...
#     API:
#         https://msdn.microsoft.com/en-us/library/office/ff837519.aspx
#     Examples:
#         http://stackoverflow.com/questions/10366596/reading-table-contetnts-in-ms-word-file-using-python

import csv
import os


CSV_FILENAME = 'tab.csv'
ENCODING = 'utf8'


# -------------------------------------------------------------------------------
#
#     Application management
#
# -------------------------------------------------------------------------------

def win32_word_dispatch():
    # Lazy import of win32com - do not load Windows/MS Office libraries when
    # they are not called.
    import win32com.client as win32
    word = win32.Dispatch("Word.Application")
    word.Visible = 0
    return word


def open_ms_word():
    try:
        return win32_word_dispatch()
    except BaseException:
        raise Exception(
            "Apparently not a Windows machine or no MS Word installed.")


def close_ms_word(app):
    app.Quit()
    # ISSUE: must also quit somewhere by calling app.Quit()
    # like in
    # http://bytes.com/topic/python/answers/23946-closing-excel-application


def open_doc(path, word):
    word.Documents.Open(path)
    return word.ActiveDocument


def get_table_count(doc):
    return doc.Tables.count


# -------------------------------------------------------------------------------
#
#     Cell value filter
#
# -------------------------------------------------------------------------------


def delete_double_space(line):
    return " ".join(line.split())


SPACE = " "
VOID = ""
APOCHAR = '"'
REPLACEMENTS = [('\r\x07', VOID)  # delete this symbol
                , ('\x0c', SPACE)  # sub with space
                , ('\x0b', SPACE)  # sub with space
                , ('\r', SPACE)  # sub with space
                , ("\u201c", APOCHAR), ("\u201d", APOCHAR), ('\x00', VOID)
                ]


def filter_cell_contents(cell_value):
    for a, b in REPLACEMENTS:
        cell_value = cell_value.replace(a, b)
    cell_value = delete_double_space(cell_value.strip())
    return cell_value


def get_filtered_cell_value(table, i, j):
    val = get_cell_value(table, i, j)
    return filter_cell_contents(val)


# -------------------------------------------------------------------------------
#
#     Word table iterators
#
# -------------------------------------------------------------------------------

def get_cell_value(table, i, j):
    try:
        return table.Cell(Row=i, Column=j).Range.Text
    # ISSUE: which specific exceptions can it throw?
    except Exception:
        return ""


def cell_iter(table):
    for i in range(1, table.rows.count + 1):
        for j in range(1, table.columns.count + 1):
            yield i, j, get_filtered_cell_value(table, i, j)


def row_iter(table):
    for i in range(1, table.rows.count + 1):
        row = []
        for j in range(1, table.columns.count + 1):
            row = row + [get_filtered_cell_value(table, i, j)]
        yield row


# -------------------------------------------------------------------------------
#
#     Document-level iterators for .doc files
#
# -------------------------------------------------------------------------------

def query_all_tables(p, func):
    word = open_ms_word()
    doc = open_doc(p, word)
    #import pdb; pdb.set_trace()
    total_tables = get_table_count(doc)
    for i, table in enumerate(doc.Tables):
        print("Reading table {} of {}...".format(i + 1, total_tables))
        yield func(table)
    close_ms_word(word)


def yield_continious_rows(p):
    for y in query_all_tables(p, func=row_iter):
        for row in y:
            yield row

# -------------------------------------------------------------------------------
#
#    Write CSV
#
# -------------------------------------------------------------------------------


def to_csv(gen, csv_path):
    """Accept iterable of rows and write in to csv_path"""
    with open(csv_path, 'w', encoding=ENCODING) as csvfile:
        filewriter = csv.writer(csvfile, delimiter='\t', lineterminator='\n')
        for row in gen:
            filewriter.writerow(row)

# -------------------------------------------------------------------------------
#
#    Folder-level batch job
#
# -------------------------------------------------------------------------------


def yield_rows_from_many_files(file_list):
    """Iterate by row over .doc files in *file_list* """
    print("Starting reading .doc files...")
    for p in file_list:
        if os.path.exists(p):
            print("File:", p)
            for row in yield_continious_rows(p):
                yield row


def get_csv_filename(folder):
    return os.path.join(folder, CSV_FILENAME)


def dump_doc_files_to_csv(file_list, csv_path):
    """Write tables from .doc in *file_list* into one *csv_path* file. """
    folder_iter = yield_rows_from_many_files(file_list)
    to_csv(folder_iter, csv_path)


def make_file_list(folder):
    files = ["tab.doc"] + ["tab{0:d}.doc".format(x) for x in range(1, 5)]
    return [os.path.abspath(os.path.join(folder, fn)) for fn in files]


def folder_to_csv(folder):
    """Make single csv based on 5 .doc files in *folder*. """
    print("\nFolder:\n    ", folder)
    file_list = make_file_list(folder)
    csv_filename = get_csv_filename(folder)
    dump_doc_files_to_csv(file_list, csv_filename)
    print("Finished creating raw CSV file:", csv_filename)


if __name__ == "__main__":
    from run_word import get_word_folder
    from pathlib import Path
    WORD_ROOT = Path("D:/digital/kep_data2")
    word_folder = get_word_folder(2012, 11, WORD_ROOT)
    folder_to_csv(word_folder)
