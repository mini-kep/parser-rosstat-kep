"""Must make_label() to separate file to avoid circular reference."""

def make_label(name: str, unit: str):
    return '{}_{}'.format(name, unit)
