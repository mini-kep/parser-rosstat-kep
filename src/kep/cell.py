#import re
#
#COMMENT_CATCHER = re.compile("\D*([\d.,]*)\s*(?=\d\))")
#def kill_comment(text, rx=COMMENT_CATCHER):
#    return rx.match(text).groups()[0]
#
#assert kill_comment('6762,31)2)') == '6762,3'     
#assert kill_comment('6762.31)2)') == '6762.3'   
#
#def as_float(text):
#    try:
#        return float(text)
#    except ValueError:
#        raise ValueError("Cannot parse to float: <{}>".format(text))
#    
#def filter_value(text):
#    # TODO: refactor this function 
#    """Converts *text* to float number assuming it may contain 'comment)'  
#       or other unexpected contents."""
#    if not text:
#        return None            
#    if text == "" or text == "…" or text=="-":
#        return None
#    if " " in text and not text.startswith(" "):
#        return filter_value(text.split(" ")[0]) 
#    if ')' in text:
#        text = kill_comment(text)
#    if text.endswith(","): # 97.1.
#        text=text[:-1] 
#    return as_float(text.replace(",", "."))
#
#assert filter_value('6762,31) 6512,3 ') == 6762.3
#    
#if __name__ == "__main__":
#    from parse import all_values
#    for text in all_values():
#        filter_value(text)

import re

# Regex:
#   \D*        any number of non-digits
#   (\d+(.|,)?\d+)  at least one digit, follow by optional dot `.` or comma `,` and then any number of digits
#   \s*        any number of whitespaces
#   (?=\d\))   follow by a digit `\d` and a closing parenthesis `)`

   
## COMMENT_CATCHER = re.compile("\D*(\d+[.,]?\d+)\s*(?=\d\))")
#def kill_comment(text, rx=COMMENT_CATCHER):
#    result = rx.match(text)
#    if result is None:
#        return text
#    return rx.match(text).groups()[0]
#
#assert kill_comment('6762,31)2)') == '6762,3'
#assert kill_comment(')') == ")"

def filter_value():
    pass

COMMENT_CATCHER = re.compile("\D*([\d., ]*)\s*(?=\d\))")     
def to_float(text, i=0):
    i += 1
    if i>5:
        raise ValueError("Max recursion depth exceeded on '{}'".format(text))
    if not text:
        return False
    text = text.replace(",", ".")  
    try:
         return float(text)
    except ValueError:
         if ")" in text: 
             text = COMMENT_CATCHER.match(text).groups()[0]
             return to_float(text, i)
         if " " in text.strip():
             return to_float(text.strip().split(" ")[0], i)
         if text.endswith(".") or text.endswith(",") :  # 97.1.
             return to_float(text[:-1], i)
         return False

for x in [None, "", " ", "…", "-", "a", "ab", " - "]:
    assert to_float(x) == False

assert to_float('5.678,') == 5.678
assert to_float('5.678,,') == 5.678
assert to_float("5.6") == 5.6
assert to_float("5,6") == 5.6
assert to_float('57,0') == 57.0
assert to_float("5,67") == 5.67
assert to_float("5,67,") == 5.67
assert to_float('123,0 4561)') == 123
assert to_float('6762,31)2)') == 6762.3
assert to_float('1734.4 1788.42)') == 1734.4

# test values not encountered in text
#assert filter_value("5.61test)2") == False
#assert filter_value("5.6test)") == False
#assert filter_value('6762,31) abc ') == 6762.3
#assert kill_comment("abc5.6 2)") == "5.6"
#assert kill_comment("abc5.6123 2)") == "5.6123"
#assert kill_comment("abc5.6123 2)3") == "5.6123"
#assert kill_comment("abc5.6123 2)34") == "5.6123"
#assert kill_comment("5.61test)2") == "5.61test)2" #not matched, should return source text as is
#assert kill_comment(")") == ")" #not matched, should return source text as is

    
if __name__ == "__main__":

    errors = ["5.678,,", '75.32)', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '84.23)', '73.23)', '83.54)', '73.04)', '84.94)', '73.44)', '100.53)', '106.21)', '106.11)', '104.91)', '107.41)', '100.91)', '101.21)', '100.91)', '100.61)', '101.71)', '101.11)', '101.01)', '102.81)', '1335.71)', '450.51)', '103.32)', '104.12)', '…', '94.61)', '96.81)', '106.92)', '413.92)', '442.62)', '104.22)', '95.31)', '97.81)', '96.82)', '106.92)', '94.22)', '93.22)', '4742.31)', '776.52)', '1102.22)', '1169.02)', '1688.42)', '5637.31)', '653.22)', '1047.52)', '1321.72)', '2606.32)', '1761.31)', '137.52)', '307.32)', '401.12)', '908.52)', '933.61)', '58.62)', '154.62)', '211.32)', '505.82)', '676.61)', '67.22)', '131.42)', '160.72)', '314.82)', '51.21)', '33.81)', '105.41)', '140.61)', '2.81)', '2.81)', '3.01)', '2.61)', '5.81)', '2.51)', '2.11)', '2.41)', '5.61)', '2.31)', '2.31)', '2.51)', '2.31)', '4.11)', '2.11)', '2.21)', '3.61)', '2.11)', '2.21)', '2.01)', '4.21)', '2.21)', '2.11)', '3.81)', '2.31)', '2.11)', '3.91)', '2.41)', '2.11)', '2.31)', '3.61)', '2.11)', '2.21)', '2.91)', '2.11)', '3.21)', '2.51)', '2.21)', '2.61)', '2.21)', '2.61)', '2.31)', '2.51)', '2.31)', '2.51)', '2.31)', '2.41)', '81.53)', '74.23)', '…', '6512.3 6762.32)', '1515.8 1587.12)', '1592.2 1656.02)', '1669.9 1730.82)', '1734.4 1788.42)', '504.1 530.52)', '516.8 543.72)', '527.1 555.52)', '525.6 543.82)', '539.5 556.72)', '555.5 575.22)', '559.5 580.52)', '554.9 575.02)', '565.5 582.32)', '569.1 584.62)', '599.8 621.52)', '2103.23)', '722.53)', '100.24)', '100.14)', '93.33)', '88.13)', '94.14)', '104.94)', '…', '122.82)', '943641)', '254881)', '41021)', '97.31)', '95.31)', '100.11)', '366641)', '384831)', '392532)', '107.12)', '107.62)', '106.73)', '88.91)', '74.01)', '92.12)', '106.92)', '102.03)', '102.43)', '103.23)', '102.52)', '82.21)', '71.31)', '91.03)', '106.83)', '101.72)', '12045.12)', '12402.62)', '14408.03)', '17425.63)', '12893.22)', '76.42)', '111.24)', '107.24)', '100.34)', '115.95)', '140.25)', '74.05)', '97.1.', '112.04)', '137.34)', '99.13)', '96.63)', '114.54)', '139.34)', '73.84)', '78.11)', '51.11)', '72.41)', '49.31)', '72.91)', '50.71)', '22.91)', '21.71)', '20.31)', '15.91)', '15.11)', '14.11)']
    for text in errors:
        z = to_float(text)
        print("assert to_float('{}') == {}".format(text, z))

    import parse
    for text in parse.all_values():
        z = to_float(text)
        print("assert to_float('{}') == {}".format(text, z))        
        
        