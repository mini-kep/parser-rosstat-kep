import re

_COMMENT_CATCHER = re.compile("\D*([\d.,]*)\s*(?=\d\))")
def kill_comment(text):
    return _COMMENT_CATCHER.match(text).groups()[0]


def as_float(text):
    try:
        return float(text)
    except ValueError:
        import pdb; pdb.set_trace() 
        raise ValueError("Cannot parse to float: <>".format(text))
    
def filter_value(text):
    """Converts *text* to float number assuming it may contain 'comment)'  
       or other unexpected contents."""
    if not text:
        return None       
    if text == "" or text == "…":
        return None
    if " " in text and not text.startswith(" "):
        return filter_value(text.split(" ")[0]) 
    if ')' in text:
        text = kill_comment(text)
    return as_float(text.replace(",", "."))
        
assert kill_comment('6762,31)2)') == '6762,3'     
assert kill_comment('6762.31)2)') == '6762.3'   
assert filter_value('6762,31) 6512,3 ') == 6762.3  
    
    
# TODO: integrate with  kill_comment(text) in kep.py 
def get_year(string: str):
    """Extract year from string *string*. 
       Return None if year is not valid or not in plausible range."""
    # Regex: 
    #   (\d{4})    4 digits
    #   \d+\)      comment like "1)"
    #   (\d+\))*   any number of comments 
    #   \s*        any number of whitespaces
    match = re.match(r'(\d{4})(\d+\))*\s*', string)
    if match:
        year = int(match.group(1))
        if year >= 1991:
            return year
    return None