import re

COMMENT_CATCHER = re.compile("\D*(\d+[.,]?\d*)\s*(?=\d\))")


def to_float(text: str, i=0):
    """Convert *text* to float() type.

    Returns:
        Float value,
        None if not successful.
    """
    i += 1
    if i > 5:
        raise ValueError("Max recursion depth exceeded on '{}'".format(text))
    if not text:
        return None
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        # note: order of checks important
        # get first value '542,0 5881)'
        if " " in text.strip():
            return to_float(text.strip().split(" ")[0], i)
        # catch '542,01)'
        if ")" in text:
            match_result = COMMENT_CATCHER.match(text)
            if match_result:
                text = match_result.group(0)
                return to_float(text, i)
        # catch 97.1, as converted to 97.1. above
        if text.endswith("."):
            return to_float(text[:-1], i)
        return None
