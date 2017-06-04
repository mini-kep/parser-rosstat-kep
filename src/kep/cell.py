import re

COMMENT_CATCHER = re.compile("\D*([\d.,]*)\s*(?=\d\))")
def kill_comment(text, rx=COMMENT_CATCHER):
    return rx.match(text).groups()[0]

assert kill_comment('6762,31)2)') == '6762,3'     
assert kill_comment('6762.31)2)') == '6762.3'   

def as_float(text):
    try:
        return float(text)
    except ValueError:
        print("<" + text + ">")
        raise ValueError("Cannot parse to float: <>".format(text))
    
def filter_value(text):
    # TODO: refactor this function 
    """Converts *text* to float number assuming it may contain 'comment)'  
       or other unexpected contents."""
    if not text:
        return None            
    if text == "" or text == "…" or text=="-":
        return None
    if " " in text and not text.startswith(" "):
        return filter_value(text.split(" ")[0]) 
    if ')' in text:
        text = kill_comment(text)
    if text.endswith(","): # 97.1.
        text=text[:-1] 
    return as_float(text.replace(",", "."))

assert filter_value('6762,31) 6512,3 ') == 6762.3
    
if __name__ == "__main__":
    from parse import all_values
    for text in all_values():
        filter_value(text)
    
    
    
    
    
    