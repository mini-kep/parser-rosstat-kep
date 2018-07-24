import kep

def read_dataframes(csv_path: str):
    values = kep.to_values(csv_path, kep.UNITS, kep.NAMERS)
    return kep.unpack_dataframes(values)



if __name__ == '__main__':
    from paths import PATH_CSV 
    tables = kep.reader.import_tables(PATH_CSV)
    reviewer = kep.reader.TableList(tables)
    n = [x for x in kep.NAMERS if x.name=='EXPORT_GOODS'][0]
    subtabs = reviewer.segment(n.starts, n.ends) 
    print (subtabs.labels)
    subtabs.parse(unit_mapper_dict=kep.UNITS, namers=[n]) 
    print (subtabs.labels)
    assert subtabs.labels == ['EXPORT_GOODS_bln_usd']
    assert n.labels == subtabs.labels
    # TODO: may check that labels equal exactly the required labels
    # TODO: namer may optionally have units mapper
    # TODO: namer to have sorted labels
    values = kep.reader.to_values2(PATH_CSV, kep.UNITS, kep.NAMERS)
    
    
    
    
    
    #print(reviewer.find('PPI', 'mln_rub'))
    #print(reviewer.labels)
    
   

# WIP:
#  - full new defintion of parsing_defintion.py
#  - convert to tests

# TODO - OTHER:
# - code review
# - run over many csv files: tab.csv and tab_old.csv + alldata/interim files

# WONTFIX:
#  - datapoint checks
#  - checking dataframes
#  - saving to disk
#  - clean notebook folders
#  - check a defintion against file (no duplicate values) - Namer.inspect()
#  - header found more than once in tables
#  - duplicate PPI_mln_rub
#  - special 12m - a  situation
#  - 1.7. Объем работ по виду деятельности ""Строительство - requires supress_apos()
#  - more definitions

# DONE
#  - type conversions and comment cleaning
#  - assert schema on namer imports
#  - write expected values
#  - timeit