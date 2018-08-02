"""Filter values in CSV file."""
import re


years = "|".join([str(x) for x in range(1999,2018+1)])
REGEX_Y = re.compile(f"({years})")
# FIXME: regex below is not good
REGEX_V = re.compile(r'(\d*?[.,]?\d*?)(\d\))*\s*$')


def is_year(string: str) -> bool:
    return clean_year(string) is not None


def clean_year(year: str) -> int:
    try: 
        x = re.findall(REGEX_Y, year)[0]
        return int(x)
    except IndexError:
        return None


def clean_value(x: str) -> float:    
    if x: 
        x = x.replace(',', '.')
        return float(re.search(REGEX_V, x).group(1))
    return None


def is_allowed(x):    
    return '______________________' not in x[0]

# kill annotations like
# "______________________ 1) Индекс промышленного производства исчисляется по видам деятельности ""Добыча полезных ископаемых"", ""Обрабатывающие производства"", ""Производство и распределение электроэнергии, газа и воды"" на основе динамики производства важнейших товаров-представителей (в натуральном или стоимостном выражении). В качестве весов используется структура валовой добавленной стоимости по видам экономической деятельности 2008 базисного года. С учетом поправки на неформальную деятельность. / Industrial Production index covers ""Mining and quarrying"", ""Manufacturing"" and "" Electricity, gas and water supply"" using changes in production of major goods-representatives (in physical and value measures). The structure of Gross value added by economic activities of 2008 base year is used as weights. Data are adjusted to informal activity."																	



def is_omission(x: str) -> bool:
    """True if *x* is any of ['', '…', '-']"""
    return x in ['', '…', '-']