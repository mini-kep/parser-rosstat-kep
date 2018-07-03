"""
Read a text string with CSV data as list of lists with:
    text_to_list()

"""

import csv
from io import StringIO

CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')


def yield_csv_rows(csv_text, fmt=CSV_FORMAT):
    """Yield CSV rows from *csvfile*.

    Args:
        csvfile - file connection or StringIO

    Yields:
        list of strings
    """
    filelike = StringIO(csv_text)
    for row in csv.reader(filelike, **fmt):
        yield row


def is_valid_row(row):
    """Check conditions:
       - *row* list is not empty
       - first element in list is not empty and is not None
       - first element does not start with underscore ____
    """
    if row:
        x = row[0]
        return x is not None and  \
            x != '' and \
            not x.startswith("___") and \
            'В целях обеспечения статистической сопоставимости' not in x
    else:
        return False


def supress_apos(text):
    return text.replace('"', '')


def clean_rows(csv_rows: list):
    return list(filter(is_valid_row, csv_rows))


def read_csv(csv_text: str):
    csv_text = supress_apos(csv_text)
    rows = yield_csv_rows(csv_text)
    return clean_rows(rows)


def pop_rows(rows, start, end):
    """Pops elements of *self.rows* between [start, end).

    Pops elements from *self.rows* that are between
    start bound (inclusive) and end bound (non-inclusive).
    Recognises element occurrences by index *i*.
    Modifies *self.rows*.

    Args:
        start: str defining start bound. e.g.:
            "1.6. Инвестиции в основной капитал",
        end: str defining end bound. e.g:
            "1.6.1. Инвестиции в основной капитал организаций"

    Returns:
        A list of rows instances between [start, end) that
        are taken out of the stack.
    """
    we_are_in_segment = False
    segment = []
    i = 0
    while i < len(rows):
        row = rows[i]
        if row[0].startswith(start):
            we_are_in_segment = True
        if row[0].startswith(end):
            break
        if we_are_in_segment:
            segment.append(row)
            del rows[i]
            # index i does not increase because it is consumed by delete
        else:
            # else is very important, indexing goes wrong without it
            i += 1
    return segment


if __name__ == "__main__":
    doc = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""
