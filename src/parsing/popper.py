"""
Read a text string with CSV data as list of lists with:
    text_to_list()

Use Popper class as a stack to split CSV data.

"""

import csv
from io import StringIO

CSV_FORMAT = dict(delimiter="\t", lineterminator="\n")


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
            not 'В целях обеспечения статистической сопоставимости' in x
    else:
        return False

def text_to_list(csv_text: str):
    csv_rows = filter(is_valid_row, yield_csv_rows(csv_text))
    return list(csv_rows)

#utils
class Text(object):    
    @staticmethod
    def supress_apos(text):
        return text.replace('"', '')    
    
    def __init__(self, text):
        self.text = self.supress_apos(text)
        
    def startswith(self, start: str):
        start = self.supress_apos(start)
        return self.text.startswith(start)

class Popper:
    """Stack for CSV rows.

      Encapsulates a list of Row class instances. Used to obtain segments of
      CSV file corresponding to parsing instruction scopes.

      Methods to extract segments of CSV file:
         self.pop(start, end) 
         self.remaining_rows()          

    """

    def __init__(self, csv_text: str):
        self.rows = text_to_list(csv_text)

    def remaining_rows(self):
        """Pops a list of rows that remain in the stack"""
        remaining = self.rows
        self.rows = []
        return remaining

    def pop(self, start, end):
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
        while i < len(self.rows):
            row = self.rows[i]
            t = Text(row[0])
            if t.startswith(start):
                we_are_in_segment = True
            if t.startswith(end):
                break
            if we_are_in_segment:
                segment.append(row)
                del self.rows[i]
                # index i does not increase because it is consumed by delete
            else:
                # else is very important, indexing goes wrong without it
                i += 1
        return segment


def find(text, csv_rows):
    does_start = lambda s: Text(s).startswith(text)
    return any(map(does_start, csv_rows))

assert find('a', ['a', 'b', 'k', 'zzz']) is True
assert find('k', ['n', 'a', 'k', 'zzz']) is True
assert find('j', ['aj', 'b', 'k', 'zzz']) is False


def get_boundaries(boundaries, rows):
    row_starts = [r[0] for r in rows]
    error_messages = ['Start or end boundary not found:']    
    for boundary in boundaries:
        s_flag = find(boundary['start'], row_starts)
        e_flag = find(boundary['end'], row_starts)
        if s_flag and e_flag:
            return boundary['start'], boundary['end']
        error_messages.extend([boundary['start'][:10], 
                               boundary['end'][:10]
                               ])
    raise ValueError('\n'.join(error_messages))


def yield_parsing_jobs(csv_text: str, definition_default, definitions_by_segment):
    stack = Popper(csv_text)
    for pdef in definitions_by_segment:
        start, end = get_boundaries(pdef.boundaries, stack.rows)
        yield stack.pop(start, end), pdef
    yield stack.remaining_rows(), definition_default


if __name__ == "__main__":
    DOC = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""
    rows = text_to_list(DOC)
    assert len(rows) == 3
    p = Popper(DOC)
    p.remaining_rows()
    p.pop('a', 'b')
