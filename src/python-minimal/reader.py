# Parse data from CSV files


# PSEUDOCODE
# ---------- 
# 1. read CSV
# 2. extract individual tables form CSV
# 3. for reach table:
#   3.1. select variable label based on name and unit strings contained in table header
#   3.2. get data from table based on columns format like "YQQQQMMMMMMMMMMMM"
# 4. combine data from tables into three dataframes based on frequency (dfa, dfq, dfm)
# 5. write dfa, dfq, dfm as csv files to disk 

# MINIMAL EXAMPLE
# ---------------

def read_csv(file): 
    """Read csv file as list of lists / matrix"""
    import csv
    fmt=dict(delimiter='\t', lineterminator='\n')
    table = []
    with open(file, 'r', encoding='utf-8') as f:
        for row in csv.reader(f, **fmt):
            table.append(row)
    return table


def is_year(x: str):
    """Simplified filter for numeric value in first column"""
    return x.startswith('199') or x.startswith('20')  

    
if __name__ == "__main__":
    # read csv    
    table = read_csv("tab.csv")
   
    def extract_table_segment(table, start_line_contain, table_end_marker):
        table_segment = []
        we_are_in_segment = False
        i = 0
        while i <= len(table):
            row = table[i]
            if start_line_contains in row[0]:
                we_are_in_segment = True
            if we_are_in_segment:
                table_segment.append(row)
                del table[i]
            else:    
                i += 1                
            if row[0].strip().startswith(table_end_marker):
                break

        return table_segment   

    start_line_contains = "Объем ВВП"
    table_end_marker = "2018"  
    segment1 = extract_table_segment(table, start_line_contains, table_end_marker)
    # current checkpoint - we were able to cut segment1 a segment from table
    #                     based on start_line_contains and table_end_marker
    
    
    #slice_data, slice_header = extract(table, start_line_contains, table_endwith)
    
    
    # next:
    # name_mapper is a dictionary that maps "Объем ВВП" to "GDP"
    # unit_mapper is a dictionary that maps "млрд.рублей" to  "bln_rub"
    
    
    # name = get_name(name_mapper, slice_header) 
    # unit = get_unit(unit_mapper, slice_header)
    # label is name_unit
    _label = "GDP_bln_rub"
    
    # get_datapoints(data=slice_data, row_pattern="YQQQQ", label=_label)
    # sort to streams of annual, quarterly and monthly data 
    
    
    # ENHANCEMENTS
    # ------------
    # - write test for minimal example
    # - same without table_endswith - stop table before when next text is encountered
    # - trailing tables like "Индекс промышленного производства" + "в % к предыдущему периоду"
    # - cleaning values like "20171)"