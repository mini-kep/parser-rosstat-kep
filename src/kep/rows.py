"""Read CSV file and represent it as a stream/list of Rows() instances."""
                                                          
import csv
import re
from . import cfg

ENC = 'utf-8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')

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




class Row:
    """CSV row representation."""

    def __init__(self, row):
        self.name = row[0]
        self.data = row[1:]

    def len(self):
        return len(self.data)

    def is_datarow(self):
        return is_year(self.name)

    def startswith(self, text):
        # clean out apostrophe (")
        r = self.name.replace('"', '')
        text = text.replace('"', '')
        return r.startswith(text)
    
    # FIXME: identical to startswith?
    def matches(self, pat):
        rx = r"\b{}".format(pat)
        if re.search(rx, self.name):
            return True
        else:
            return False   

    def get_year(self):
        return get_year(self.name)      
        
    def get_varname(self, varnames_mapper_dict):
        varnames = []
        for k in varnames_mapper_dict.keys():
            if self.matches(k):
                varnames.append(varnames_mapper_dict[k])
        return self.__single_value__(varnames)
    
    def get_unit(self, units_mapper_dict = cfg.UNITS):
        for k in units_mapper_dict.keys():
            if k in self.name:
                return units_mapper_dict[k]
        return False    
    
    def __single_value__(self, values):
        """Return first element in *values* or raise ValueError.
           Returns False if *values* is empty.
        """
        if len(values)>1:
            msg = "Multiple entries found in <{}>: {}".format(self.name, values)
            raise ValueError(msg)
        elif len(values)==1:
            return values[0]
        else:
            return False

    def __eq__(self, x):
       return bool(self.name == x.name and self.data == x.data)           
              

    def __str__(self):
        if "".join(self.data):
            return "<{} | {}>".format(self.name, ' '.join(self.data))
        else:
            return "<{}>".format(self.name)

    def __repr__(self):
        return "Row {}".format([self.name] + self.data)

YEAR_CATCHER = re.compile('(\d{4}).*')


def get_year(string: str, rx=YEAR_CATCHER):
    """Extracts year from string *string*.
       Returns False if year is not valid or not in plausible range."""
    match = re.match(rx, string)
    if match:
        year = int(match.group(1))
        if year >= 1991 and year <= 2050:
            return year
    return False


def is_year(string: str) -> bool:
    return get_year(string) is not False


class Rows:
    """Holder for CSV rows. Allows extracting segments of CSV file and 
       remaining part of CSV file, after all segments are extracted."""

    def __init__(self, csv_path, reader_func=read_csv):
        # consume *rows*, likely it is a generator
        self.rows = [r for r in reader_func(csv_path)]

    def remaining_rows(self):
        return self.rows

    def pop(self, pdef):
        # walks by different versions of start/end lines 
        start, end = pdef.scope.get_boundaries(self.rows)
        return self.__pop_segment__(start, end)

    def __pop_segment__(self, start, end):
        """Pops elements of self.rows between [start, end).
           Recognises element occurrences by index *i*.
           Modifies *self.rows*.
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
    
if __name__ == "__main__":
    assert Row(["1. abcd"]).get_varname({'1. ab':"ZZZ"}) == 'ZZZ'
    assert Row(["1. abcd"]).get_varname({'bc':"ZZZ"}) is False
    import pytest       
    with pytest.raises(ValueError):
         assert Row(["1. abcd"]).get_varname({'1. ab':"ZZZ", '1. abcd':"YYY"}) 
    assert Row(["1. abcd, %"]).get_unit({'%':"pct"}) == 'pct'     

     
    def mock_read_csv(_):
        yield Row(["apt", "1", "2"])
        yield Row(["bat aa...ah", "1", "2"])
        yield Row(["can", "1", "2"])
        yield Row(["dot oo...eh", "1", "2"])
        yield Row(["wed", "1", "2"])
        yield Row(["zed"])
    
    rows = Rows(None, mock_read_csv)
    a = rows.__pop_segment__("bat", "dot")
    assert len(a) == 2      
    b = rows.__pop_segment__("apt", "wed")  
    assert len(b) == 2    
    c = rows.remaining_rows()
    assert c[0] == Row(['wed', '1', '2'])
    assert c[1] == Row(['zed'])
         