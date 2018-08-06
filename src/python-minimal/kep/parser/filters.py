"""Filter digits from CSV file.

Bad friends:
    
    '1001)' (a comment)
    '1001)2)' (two comments)
    '…' (omission)
    '-' ()

"""
import re
from datetime import date


def make_regex_annual(start=1999, end=date.today().year):
    rng = [str(x) for x in range(start,end+1)]
    years = "|".join(rng)
    return re.compile(f"({years})")
    
REGEX_ANNUAL = make_regex_annual()

def clean_year(year: str) -> int:
    try: 
        x = re.findall(REGEX_ANNUAL, year)[0]
        return int(x)
    except IndexError:
        return None

# FIXME: regex below is not too good
REGEX_DIGITS = re.compile(r'(\d*?[.,]?\d*?)(\d\))*\s*$')

def clean_value(x: str) -> float:    
    if x: 
        x = x.replace(',', '.')
        z = re.search(REGEX_DIGITS, x).group(1)
        return float(z)
    return None


def is_omission(x: str) -> bool:
    """True if *x* is any of ['', '…', '-']"""
    return x in ['', '…', '-']