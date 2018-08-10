"""Display parsing result description."""

from scan import underscore, names, varcount, labels

def filtered_labels(label_list, name):
    labels = [(name, unit) for _name, unit in label_list if _name == name] 
    return list(map(underscore, labels))

def with_comma(items):
    return ", ".join(items)

def cover(tables, group_dict):
    in_yaml = all_names(group_dict)
    in_tables = names(tables)
    return (set(in_yaml)-set(in_tables) or '' , 
            set(in_tables)-set(in_yaml) or '')  
    
def all_names(group_dict):
        return set([x for _names in group_dict.values() for x in _names])    
    
def print_reference(tables, group_dict):
    print(varcount(tables), "variables and", len(tables), "labels")
    label_list = labels(tables)
    name_list = names(tables)
    for group_header, group_names in group_dict.items():
        print(group_header)
        for name in group_names:            
            if name in name_list:                
                msg = with_comma(filtered_labels(label_list, name))            
                print("    {} ({})".format(name, msg))  
    missing, extras = cover(tables, group_dict)
    missing = sorted(list(missing))
    br = "\n    "
    if extras:
        print('Also found in dataset:', br, br.join(extras), sep='')
    if missing:
        print('Missing from dataset:', br, br.join(missing), sep='')