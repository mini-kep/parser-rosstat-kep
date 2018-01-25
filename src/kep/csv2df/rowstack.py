import csv
import re
from io import StringIO
from pathlib import Path

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
        return row and row[0] and not row[0].startswith("___")
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

class Rows:
    """Stack for CSV rows.

      Encapsulates a list of Row class instances. Used to obtain segments of
      CSV file w2ith corresponding parsing instructions.

      Extracts segments of CSV file by methods self.pop() and self.remaining_rows().

      Public method:

          .yield_segment_with_defintion(spec)
    """

    def __init__(self, csv_text, parsing_defintion):
        self.rows = text_to_rows(csv_text)
        self.parsing_defintion = parsing_defintion

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

    def yield_populated_defintions(self):
        """Yield CSV segments and corresponding parsing definitons.

        Yield CSV segments as Row() instances and corresponding
        parsing definitons based on *spec* parsing specification.

        Args:
            spec: parsing specification as spec.Specification() instance

        Yields:
            Parsing definiton with a *csv_segment* assigned. 
        """
        for pdef in self.parsing_defintion.segments:
            start, end = pdef.get_bounds(self.rows)
            pdef.csv_segment = self.pop(start, end) 
            yield pdef
        pdef = self.parsing_defintion.default    
        pdef.csv_segment = self.remaining_rows()
        yield pdef
  