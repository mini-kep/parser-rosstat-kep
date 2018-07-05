# EP: может этот файл должен как-то по-другому называться?

import re

# EP: get_year - более протестированная и общая функция, но может быть ее
# можно заменить на clean_year

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


# WONTFIX: use re.match()?
REGEX_Y = re.compile(r'\s*(\d{4})')


def clean_year(year: str) -> int:
    found = re.search(REGEX_Y, year)
    return int(found.group(0)) if found else None

# TODO: move to tests
assert clean_year('20052),3)') == 2005
assert clean_year('20114)') == 2011
assert clean_year('abc') is None
assert clean_year('') is None
assert clean_year('111') is None
assert clean_year('1001') == 1001

REGEX_V = re.compile(r'\s*(\d*?.?\d*?)(\d\))*\s*$')


def clean_value(x: str) -> float:
    x = x.replace(',', '.').replace('…', '')
    return float(re.search(REGEX_V, x).group(1)) if x else 0

# TODO: move to tests
assert clean_value('406911)') == 40691
assert clean_value('211,32)') == 211.3
assert clean_value('') == 0
assert clean_value('…') == 0
