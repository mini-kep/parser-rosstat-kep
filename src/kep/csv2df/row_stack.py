"""
1. Instance of Defintions() class has default and segment parsing defintions
2. InterimCSV(year, month).text has CSV as string
3. DEFINITION.attach_data

"""

import csv
from io import StringIO

from kep.csv2df.row_model import Row

CSV_FORMAT = dict(delimiter="\t", lineterminator="\n")


def yield_csv_rows_from_string(csv_text):
    return yield_csv_rows(StringIO(csv_text))


def yield_csv_rows(csvfile, fmt=CSV_FORMAT):
    """Yield CSV rows from *csvfile*.

    Args:
        csvfile - file connection or StringIO

    Yields:
        list of strings
    """
    for row in csv.reader(csvfile, **fmt):
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
               not x.startswith("___")
    else:
        return False

def text_to_list(csv_text):
    csv_rows = filter(is_valid_row, yield_csv_rows_from_string(csv_text))
    return list(csv_rows)
    


def text_to_rows(csv_text):
    """Get Row() instances from *csv_text*.

    Args:
        csvfile - file connection or StringIO

    Retruns:
        list of Row() instances
    """
    csv_rows = filter(is_valid_row, yield_csv_rows_from_string(csv_text))
    return list(map(Row, csv_rows))


class RowStack:
    """Stack for CSV rows.

      Encapsulates a list of Row class instances. Used to obtain segments of
      CSV file w2ith corresponding to parsing instructions.

      Internal methods:
        
        self.pop(start, end) and self.remaining_rows() - extracts segments of CSV file

      Public method:

          yield_populated_defintions()
    """

    def __init__(self, csv_text):
        self.rows = text_to_rows(csv_text)

    def remaining_rows(self):
        """Pops a list of Row() instances that remain in this RowStack"""
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
            A list of Row() instances between [start, end) that 
            are taken out of RowStack.
        """
        we_are_in_segment = False
        segment = []
        i = 0
        while i < len(self.rows):
            row = self.rows[i]
            if row.startswith(start):
                we_are_in_segment = True
            if row.startswith(end):
                break
            if we_are_in_segment:
                segment.append(row)
                del self.rows[i]
                # there is no *i += 1* because after delete 
                # the index refers to next row
            else:
                # else is very important, indexing goes wrong without it
                i += 1
        return segment  


class Popper:
    """Stack for CSV rows.

      Encapsulates a list of Row class instances. Used to obtain segments of
      CSV file w2ith corresponding to parsing instructions.

      Internal methods:
        
        self.pop(start, end) and self.remaining_rows() - extracts segments of CSV file

      Public method:

          yield_populated_defintions()
    """

    def __init__(self, csv_text):
        self.rows = text_to_list(csv_text)

    def remaining_rows(self):
        """Pops a list of Row() instances that remain in this RowStack"""
        remaining = self.rows
        self.rows = []
        return remaining
    
    def startswith(row, text):
        """Helper function for header parsing.

        Returns:
            True if *row[0]* starts with *text*.
            False otherwise.
        """
        # clean out apostrophe (")
        r = row[0].replace('"', '')
        text = text.replace('"', '')
        return r.startswith(text)

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
            A list of Row() instances between [start, end) that 
            are taken out of RowStack.
        """
        we_are_in_segment = False
        segment = []
        i = 0
        while i < len(self.rows):
            row = self.rows[i]
            if self.startswith(row, start):
                we_are_in_segment = True
            if self.startswith(row, end):
                break
            if we_are_in_segment:
                segment.append(row)
                del self.rows[i]
            else:
                # else is very important, indexing goes wrong without it
                i += 1
        return segment 


if __name__ == "__main__":
    DOC = """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044"""
    rows = text_to_rows(DOC)    
    assert len(rows) == 3     
  