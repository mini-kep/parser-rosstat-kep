"""Parse raw CSV file into Tables() instances using parsing specification from cfg.py

Main call:
   csv_path = locate_csv(year, month)
   tables = Tables(csv_path).get_required():

Parsing procedure:
   - cut out a segment of csv file as delimited by start and end line makers
   - hold remaining parts of csv file for further parsing
   - break csv segment into tables, each table containing headers and data rows
   - parse table headers to obtain variable name ("GDP") and unit ("bln_rub")

"""

from enum import Enum, unique
from collections import OrderedDict as odict
import csv
import itertools
import re
import warnings

import files
import splitter
# parsing specification
from cfg import SPEC
from cfg import UNITS

# use'always' or 'ignore'
warnings.simplefilter('ignore', UserWarning)


ENC = 'utf-8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')


# label handling
def make_label(vn, unit, sep="_"):
    return vn + sep + unit


def split_label(label):
    return extract_varname(label), extract_unit(label)


def extract_varname(label):
    words = label.split('_')
    return '_'.join(itertools.takewhile(lambda word: word.isupper(), words))


def extract_unit(label):
    words = label.split('_')
    return '_'.join(itertools.dropwhile(lambda word: word.isupper(), words))


# csv file access
def to_csv(rows, path):
    """Accept iterable of rows *rows* and write in to *csv_path*"""
    with path.open('w', encoding=ENC) as csvfile:
        filewriter = csv.writer(csvfile, **CSV_FORMAT)
        for row in rows:
            filewriter.writerow(row)
    return path


def from_csv(path):
    """Get iterable of rows from *csv_path*"""
    with path.open(encoding=ENC) as csvfile:
        csvreader = csv.reader(csvfile, **CSV_FORMAT)
        for row in csvreader:
            yield row


def read_csv(path):
    """Yield non-empty dictionaries with 'head' and 'data' keys from *path*"""
    raw_csv_rows = from_csv(path)
    filled = filter(lambda row: row and row[0], raw_csv_rows)
    no_comments = filter(lambda row: not row[0].startswith("___"), filled)
    return map(Row, no_comments)


class Tables:
    """Returns tables from *csv_path* by .get_all() method."""

    def __init__(self, csv_path, spec=SPEC, units=UNITS):
        rows = read_csv(csv_path)
        self.row_stack = RowStack(rows)
        self.tables = self.extract_all_tables(spec, units)
        self.required = [make_label(*req) for req in spec.required()]

    def extract_all_tables(self, spec, units):
        all_tables = []
        # use additional parsing definitions
        for pdef in spec.additional:
            csv_segment = self.row_stack.pop(pdef)
            tables = extract_tables(csv_segment, pdef, units)
            all_tables.extend(tables)
        # use default parsing definition on remaining rows
        pdef = spec.main
        csv_segment = self.row_stack.remaining_rows()
        tables = extract_tables(csv_segment, pdef, units)
        all_tables.extend(tables)
        return all_tables

    def get_defined(self):
        return [t for t in self.tables if t.is_defined()]

    def get_required(self):
        return [t for t in self.get_defined() if t.label in self.required]


def extract_tables(rows_segment, pdef, units):
    tables = [t.parse(pdef, units) for t in split_to_tables(rows_segment)]
    fix_multitable_units(tables)
    check_required_labels(tables, pdef)
    return tables


def fix_multitable_units(tables):
    """For tables without *header.varname* copy *header.varname*
       from previous table. Applies to tables that do not have
       any unknown rows.
    """
    for prev_table, table in zip(tables, tables[1:]):
        if table.header.varname is None and not table.header.has_unknown_lines():
            table.header.varname = prev_table.header.varname


def check_required_labels(tables, pdef):
    labels_required = [make_label(varname, unit)
                       for varname, unit in pdef.required]
    labels_in_tables = [t.label for t in tables]
    labels_missed = [x for x in labels_required if x not in labels_in_tables]
    if labels_missed:
        raise ValueError("Missed labels:" + labels_missed.__str__())


YEAR_CATCHER = re.compile('(\d{4}).*')


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from string *string*.
       Returns None if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991:
            return year
    return None


def is_year(string: str) -> bool:
    return get_year(string) is not None


class Row:
    """Single CSV row representation."""

    def __init__(self, row):
        self.name = row[0]
        self.data = row[1:]

    def len(self):
        return len(self.data)

    def is_datarow(self):
        return is_year(self.name)

    def matches(self, text):
        r = self.name.replace('"', '')
        text = text.replace('"', '')
        return r.startswith(text)

    def __str__(self):
        if "".join(self.data):
            return "<{} | {}>".format(self.name, ' '.join(self.data))
        else:
            return "<{}>".format(self.name)

    def __repr__(self):
        return dict(name=self.name, data=self.data).__str__()

    def equals_dict(self, d):
        return self.name == d['name'] and self.data == d['data']


class RowStack:
    """Holder for CSV rows."""

    def __init__(self, rows):
        # consume *rows*, maybe it is a generator
        self.rows = [r for r in rows]

    def is_found(self, text):
        for row in self.rows:
            if row.matches(text):
                return True
        return False

    def remaining_rows(self):
        return self.rows

    def pop(self, pdef):
        # walks by different versions of start/end lines eg 1.10... or 1.9...
        for marker in pdef.markers:
            s = marker['start']
            e = marker['end']
            if not s and not e:
                return self.remaining_rows()
            elif not s or not e:
                raise ValueError("Single None as a marker cannot be processed")
            elif self.is_found(s) and self.is_found(e):
                return self.pop_segment(s, e)
        self.echo_error_ends_not_found(pdef)
        return []

    def echo_error_ends_not_found(self, pdef):
        print("ERROR: start or end line not found in *self.rows*")
        for marker in pdef.markers:
            s = marker['start']
            e = marker['end']
            print("   ", self.is_found(s), "<{}>".format(s))
            print("   ", self.is_found(e), "<{}>".format(e))

    def pop_segment(self, start, end):
        """Pops elements of self.row between [start, end).
           Recognises element occurrences by index *i*.
           Modifies *self.rows*."""
        we_are_in_segment = False
        segment = []
        i = 0
        while i < len(self.rows):
            row = self.rows[i]
            if row.matches(start):
                we_are_in_segment = True
            if row.matches(end):
                break
            if we_are_in_segment:
                segment.append(row)
                del self.rows[i]
            else:
                # else is very important, wrong indexing without it
                i += 1
        return segment


# classes for split_to_tables()
@unique
class RowType(Enum):
    UNKNOWN = 0
    DATA = 1
    SECTION = 2
    HEADER = 3


@unique
class State(Enum):
    INIT = 1
    DATA = 2
    UNKNOWN = 3


def split_to_tables(rows):
    """Yields Table() instances from *rows*."""
    datarows = []
    headers = []
    state = State.INIT
    for row in rows:
        if row.is_datarow():
            datarows.append(row)
            state = State.DATA
        else:
            if state == State.DATA:  # table ended
                yield Table(headers, datarows)
                headers = []
                datarows = []
            headers.append(row)
            state = State.UNKNOWN
    # still have some data left
    if len(headers) > 0 and len(datarows) > 0:
        yield Table(headers, datarows)


class Table:
    """Representation of CSV table, has headers and datarows."""

    # [4, 5, 12, 13, 17]
    VALID_ROW_LENGTHS = list(splitter.ROW_LENGTH_TO_FUNC_MAPPER.keys())

    def __init__(self, headers, datarows):
        # WONTFIX: naming with three headers in one line
        self.header = Header(headers)
        self.datarows = datarows
        self.coln = max(row.len() for row in self.datarows)
        self.splitter_func = None

    def parse(self, pdef, units):
        self.header.set_varname(pdef, units)
        self.header.set_unit(units)
        self.set_splitter(pdef)
        return self

    def set_splitter(self, pdef):
        funcname = pdef.reader
        if funcname:
            # reader pdef overrides other specs
            self.splitter_func = splitter.get_custom_splitter(funcname)
        elif self.coln in self.VALID_ROW_LENGTHS:
            # use standard splitters for standard number of columns
            self.splitter_func = splitter.get_splitter(self.coln)
        else:
            # Trying to parse a table without <year> <values> structure.
            # Such tables are currently out of scope of parsing definition.
            warnings.warn(
                "Unexpected row length {}\n{}".format(
                    self.coln, self))

    @property
    def label(self):
        vn = self.header.varname
        u = self.header.unit
        if vn and u:
            return make_label(vn, u)

    def is_defined(self):
        return bool(self.label and self.splitter_func)

    def echo_error_table_not_valid(self):
        if not self.label:
            raise ValueError("Label not defined for:\n{}".format(self))
        if not self.splitter_func:
            raise ValueError("Splitter func not defined for:\n{}".format(self))

    def __str__(self):
        return "\n".join(["Table {}".format(self.label),
                          "columns: {}".format(self.coln),
                          self.header.__str__(),
                          "data:",
                          '\n'.join([row.__str__() for row in self.datarows]),
                          ])

    def __repr__(self):
        return "Table {} ".format(self.label) + \
               "(headers: {}, ".format(len(self.header.textlines)) + \
               "datarows: {})".format(len(self.datarows))


class Header:
    """Table header. Can extract variable label."""

    KNOWN = "+"
    UNKNOWN = "-"

    def __init__(self, rows):
        self.varname = None
        self.unit = None
        self.textlines = [row.name for row in rows]
        self.processed = odict((line, self.UNKNOWN) for line in self.textlines)

    def set_varname(self, pdef, units):
        varname_dict = pdef.headers
        known_headers = varname_dict.keys()
        for line in self.textlines:
            just_one = 0
            for header in known_headers:
                rx = r"\b" + header
                if re.search(rx, line):
                    just_one += 1
                    self.processed[line] = self.KNOWN
                    self.varname = varname_dict[header]
                    unit = self.extract_unit(line, units)
                    if unit:
                        self.unit = unit
                    else:
                        # Trying to extract unit of measurement from a header without it.
                        # Usually a proper unit is found in next few header
                        # textlines.
                        warnings.warn("unit not found in  <{}>".format(line))
            # anything from known_headers must be found only once
            assert just_one <= 1

    @staticmethod
    def extract_unit(line, units):
        for k in units.keys():
            if k in line:
                return units[k]
        return None

    def set_unit(self, units):
        for line in self.textlines:
            unit = self.extract_unit(line, units)
            if unit:
                self.unit = unit
                self.processed[line] = self.KNOWN
                # FIXME: maybe it does not matter where the line was found?
                # if unit was found at the start of line, mark line as known
                # for u in units.keys():
                #    if line.startswith(u):
                #        self.processed[line] = self.KNOWN

    def has_unknown_lines(self):
        return self.UNKNOWN in self.processed.values()

    def __str__(self):
        show = ["varname: {}, unit: {}".format(self.varname, self.unit),
                "headers:"] + \
            ["{} <{}>".format(v, k) for k, v in self.processed.items()]
        return "\n".join(show)

# regression tests - after bug fixes on occasional errors
def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=ENC)
    assert "\0" not in z
    
if __name__ == "__main__":
    csv_path = files.locate_csv()
    tables = Tables(csv_path).get_required()
    for t in tables:
        print()
        print(t)
