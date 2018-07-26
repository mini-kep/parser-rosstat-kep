# must be in separate file to avoid circular reference
def make_label(name: str, unit: str):
    return '{}_{}'.format(name, unit)


def iterate(x):
    """Mask single string as list."""
    if isinstance(x, str):
        return [x]
    else:
        return x
