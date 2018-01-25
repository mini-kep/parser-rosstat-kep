"""
1. Instance of Defintions() class has default and segment parsing defintions
2. InterimCSV(year, month).text has CSV as string
3. DEFINITION.attach_data

"""

import csv
from io import StringIO

from kep.csv2df.reader import Row

ENC = "utf-8"
CSV_FORMAT = dict(delimiter="\t", lineterminator="\n")

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
       - *row* listis not empty
       - first element in list is not empty
       - first element does not start with underscore ____
    """
    try:
        return (len(row)>0 
                and row[0] is not None 
                and not row[0].startswith("___")
                )
    except IndexError:
        return False


def text_to_rows(csv_text):
    """Get Row() instances from *csv_text*.

    Args:
        csvfile - file connection or StringIO

    Retruns:
        list of Row() instances
    """
    filelike = StringIO(csv_text)
    csv_rows = filter(is_valid_row, yield_csv_rows(filelike))
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
            else:
                # else is very important, indexing goes wrong without it
                i += 1
        return segment  

if __name__ == "__main__":
    rows = text_to_rows("""Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")    
    assert len(rows) == 3 
    
  