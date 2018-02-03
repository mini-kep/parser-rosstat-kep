"""Read CSV file and represent it as a list of Row class instances."""

import re

YEAR_CATCHER = re.compile("\D*(\d{4}).*")


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


def is_datarow(row):
    return is_year(row[0])


def header(row):
    return row[0]


def data(row):
    return row[1:] 


def matches(string, pattern):
    """Helper function for header parsing.

    Returns:
        True if *self.name* contains *text*.
        False otherwise.
    """
    regex = r"\b{}".format(pattern)
    return bool(re.search(regex, string))


def get_varname(row, mapper_dict):
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
    header = header(row)
    varnames = [mapper_dict[key] for key in mapper_dict.keys() if matches(header, key)] 
    if len(varnames) > 1:
        msg = "Multiple entries found in <{0}>: {1}".format(header, varnames)
        raise ValueError(msg)
    elif len(varnames) == 1:
        return varnames[0]
    else:
        return False


def get_unit(row, units_mapper_dict):
    """Returns unit of measurement for this row.

    Args:
        units_mapper_dict: dictionary of valid units of measurement,
                           ex. {'% change from previous period': 'rog',
                                'billion ruble': 'bln_rub'}

    Returns:
        Matched unit of measurement as string.
        False if no match was found.
    """
    header=header(row)
    for k in units_mapper_dict.keys():
        if k in header:
            return units_mapper_dict[k]
    return False


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
        """Returns unit of measurement for this row.

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
