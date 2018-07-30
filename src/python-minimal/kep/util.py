import calendar


def make_label(name: str, unit: str):
    """Concat variable name and unit.

       Placed in a separate file to avoid circular reference.
    """
    return '{}_{}'.format(name, unit)


def iterate(x):
    """Mask single string as list."""
    if isinstance(x, str):
        return [x]
    else:
        return x


def last_day(year, month):
    return calendar.monthrange(year, month)[1]


def timestamp(year, month):
    """Make end of month YYYY-MM-DD timestamp."""
    day = last_day(year, month)
    return f'{year}-{str(month).zfill(2)}-{day}'