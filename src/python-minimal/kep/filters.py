import re

# дублирование: get_year - более протестированная и общая функция, но может быть ее
# можно заменить на clean_year

YEAR_CATCHER = re.compile("\D*(\d{4}).*")
REGEX_Y = re.compile(r'\s*(\d{4})')
# FIXME: had comments this regex may not be good:
REGEX_V = re.compile(r'\s*(\d*?.?\d*?)(\d\))*\s*$')

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


def clean_year(year: str) -> int:
    found = re.search(REGEX_Y, year)
    if found: 
        return int(found.group(0)) 
    return None


def clean_value(x: str) -> float:
    x = x.replace(',', '.')
    if x: 
        return float(re.search(REGEX_V, x).group(1))
    return None


def is_omission(x):
    return x in ['', '…', '-']