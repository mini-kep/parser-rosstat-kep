"""Read CSV file and represent it as a list of Row class instances."""

import csv
import re
from io import StringIO
from pathlib import Path

ENC = "utf-8"
CSV_FORMAT = dict(delimiter="\t", lineterminator="\n")


def make_segment_definitions(pdef_list):
    return [pdef for pdef in pdef_list if pdef.scope]


def first_unbounded_definition(pdef_list):
    try:
        return [pdef for pdef in pdef_list if not pdef.scope][0]
    except IndexError:
        return None


def get_segment_with_pdef(path, pdef_list):
    text = path.read_text(encoding=ENC)
    return get_segment_with_pdef_from_text(text, pdef_list)


def get_segment_with_pdef_from_text(text, pdef_list):
    """Get CSV file segments with corresponding parsing defintions
       from CSV file and parsing specification.

       A CSV file segment is a list of Row class instances.

       Pasring specification contains segment boundaries and
       parsing defintions by segment.
    """
    incoming = StringIO(text)
    rows = to_rows(incoming)
    rowstack = RowStack(rows)
    if not isinstance(pdef_list, list):
        pdef_list = [pdef_list]
    pdef_default = first_unbounded_definition(pdef_list)
    pdef_segments = make_segment_definitions(pdef_list)
    return rowstack.yield_segment_with_defintion(pdef_default, pdef_segments)


# csv file access
def open_csv(path):
    """
    Args:
        path (pathlib.Path) - path to csv file with data
    """
    if isinstance(path, Path):
        return path.open(encoding=ENC)
    else:
        raise TypeError(f'<{path}> should be pathlib.Path() instance')


def yield_csv_rows(csvfile, fmt=CSV_FORMAT):
    """Yield CSV rows from *csvfile*.

    Args:
        csvfile - file connection or StringIO

    Yields:
        list of strings
    """
    for row in csv.reader(csvfile, **fmt):
        yield row


def filter_csv_rows(gen):
    """Kill empty rows and rows with comments from *gen*."""
    filled = filter(lambda row: row and row[0], gen)
    no_comments = filter(lambda row: not row[0].startswith("___"), filled)
    return no_comments


def to_rows(csvfile):
    """Filter and yield Row() instances from *csvfile*.

    Args:
        csvfile - file connection or StringIO

    Yields:
        Row() instances
    """
    csv_rows = yield_csv_rows(csvfile)
    csv_rows = filter_csv_rows(csv_rows)
    return map(Row, csv_rows)


class Row:
    """CSV row representation.

    Encapsulates a list of strings and allows extracting
    unit and variable name from row.

    Methods:
      .get_unit(...)
      .get_varname(...)

    """

    def __init__(self, row):
        """
        Args:
            row - list of strings
        """
        self.name = row[0]
        self.data = row[1:]

    def is_datarow(self):
        """Helper function for table demarkation.

        Returns:
            True if first element in row is year.
            False otherwise.
        """
        return is_year(self.name)

    def startswith(self, text):
        """Helper function for header parsing.

        Returns:
            True if *self.name* starts with *text*.
            False otherwise.
        """
        # clean out apostrophe (")
        r = self.name.replace('"', '')
        text = text.replace('"', '')
        return r.startswith(text)

    def matches(self, pat):
        """Helper function for header parsing.

        Returns:
            True if *self.name* contains *text*.
            False otherwise.
        """
        rx = r"\b{}".format(pat)
        return bool(re.search(rx, self.name))

    def get_year(self):
        """Extract year as integer from *self.name*

        If *self.name* cannot be parsed as a year, False is returned

        Returns:
            year as an integer, or False.
        """
        return get_year(self.name)

    def get_varname(self, varnames_mapper_dict):
        """Returns variable name string (varname) found in this row.

        Args:
            varnames_mapper_dict: dictionary of valid variable names.
                                  For example: {'Gross domestic product':'GDP'}

        Returns:
            Matched varname from *self.name* as string, for example:
            'GDP', 'CPI', 'INDPRO'.

            If no match was found returns False.

        Raises:
            ValueError: if found for more than one varname .
        """
        varnames = []
        for k in varnames_mapper_dict.keys():
            if self.matches(k):
                varnames.append(varnames_mapper_dict[k])
        if len(varnames) > 1:
            msg = "Multiple entries found in <{0}>: {1}".format(
                self.name, varnames)
            raise ValueError(msg)
        elif len(varnames) == 1:
            return varnames[0]
        else:
            return False

    def get_unit(self, units_mapper_dict):
        """Returns units measurement for this row.

        Args:
            units_mapper_dict: dictionary of valid units of measurement,
                               ex. {'% change from previous period': 'rog',
                                    'billion ruble': 'bln_rub'}

        Returns:
            Matched unit of measurement as string.
            False if no match was found.
        """
        for k in units_mapper_dict.keys():
            if k in self.name:
                return units_mapper_dict[k]
        return False

    def __len__(self):
        return len(self.data)

    def __eq__(self, x):
        return bool(self.name == x.name and self.data == x.data)

    def __str__(self):
        if "".join(self.data):
            return "<{} | {}>".format(self.name, " ".join(self.data))
        else:
            return "<{}>".format(self.name)

    def __repr__(self):
        return "Row({})".format([self.name] + self.data)


YEAR_CATCHER = re.compile("(\d{4}).*")


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from *string* using *rx* regex.

       Returns:
           Year as integer
           False if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991 and year <= 2050:
            return year
    return False


def is_year(string: str) -> bool:
    return get_year(string) is not False


class RowStack:
    """Stack for CSV rows.

      Encapsulates a list of Row class instances. Used to obtain segments of
      CSV file w2ith corresponding parsing instructions.

      Extracts segments of CSV file by methods self.pop() and self.remaining_rows().

      Public method:

          .yield_segment_with_defintion(spec)
    """

    def __init__(self, rows):
        self.rows = list(rows)

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
                # else is very important, wrong indexing without it
                i += 1
        return segment

    def yield_populated_defintions(self, pdef_default, pdef_segments):
        """Yield CSV segments and corresponding parsing definitons.

        Yield CSV segments as Row() instances and corresponding
        parsing definitons based on *spec* parsing specification.

        Args:
            spec: parsing specification as spec.Specification() instance

        Yields:
            Parsing definiton with a *csv_segment* assigned. 
        """
        for pdef in pdef_segments:
            start, end = pdef.get_bounds(self.rows)
            pdef.csv_segment = self.pop(start, end)            
            yield pdef
        if pdef_default:
            pdef_default.csv_segment = self.remaining_rows()
            yield pdef_default

    def yield_segment_with_defintion(self, pdef_default, pdef_segments):
        """Yield CSV segments and corresponding parsing definitons.

        Yield CSV segments as Row() instances and corresponding
        parsing definitons based on *spec* parsing specification.

        Args:
            spec: parsing specification as spec.Specification() instance

        Yields:
            Yield CSV segments (list of Row() instances)
            and parsing definiton pairs as tuples
        """
        for pdef in pdef_segments:
            start, end = pdef.get_bounds(self.rows)
            csv_segment = self.pop(start, end)
            yield csv_segment, pdef
        if pdef_default:
            yield self.remaining_rows(), pdef_default        


# if __name__ == "__main__":
#    from config import InterimCSV, LATEST_DATE
#    import csv2df.specification as spec
#
#    # print all rows from csvpath
#    year, month = LATEST_DATE
#    csv_path = InterimCSV(year, month).path
#    csvfile = open_csv(csv_path)
#    reader = Reader(csvfile, spec=spec.SPEC)
#    for csv_segment, pdef in reader.items():
#        for row in csv_segment:
#            print(row)
#    csvfile.close()
