from pathlib import Path

valid_years = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]          

available_dates = [(2009, 4), (2009, 5), (2009, 6), (2009, 7), (2009, 8), (2009, 9), 
             (2009, 10), (2009, 11), (2009, 12), 
             
             (2010, 1), (2010, 2), (2010, 3), (2010, 4), (2010, 5), (2010, 6), 
             (2010, 7), (2010, 8), (2010, 9), (2010, 10), (2010, 11), (2010, 12),
             
             (2011, 1), (2011, 2), (2011, 3), (2011, 4), (2011, 5), (2011, 6),
             (2011, 7), (2011, 8), (2011, 9), (2011, 10), (2011, 11), (2011, 12), 
             
             (2012, 1), (2012, 2), (2012, 3), (2012, 4), (2012, 5), (2012, 6), 
             (2012, 7), (2012, 8), (2012, 9), (2012, 10), (2012, 11), (2012, 12), 
             
             (2013, 1), (2013, 2), (2013, 3), (2013, 4), (2013, 5), (2013, 6), 
             (2013, 7), (2013, 8), (2013, 9), (2013, 10), # missing (2013, 11)
             (2013, 12), 
             
             (2014, 1), (2014, 2), (2014, 3), (2014, 4), (2014, 5), (2014, 6), 
             (2014, 7), (2014, 8), (2014, 9), (2014, 10), (2014, 11), (2014, 12), 
             
             (2015, 1), (2015, 2), (2015, 3), (2015, 4), (2015, 5), (2015, 6), 
             (2015, 7), (2015, 8), (2015, 9), (2015, 10), (2015, 11), (2015, 12), 
             
             (2016, 1), (2016, 2), (2016, 3), (2016, 4), (2016, 5), (2016, 6), 
             (2016, 7), (2016, 8), (2016, 9), (2016, 10), (2016, 11), (2016, 12), 
             
             (2017, 1), (2017, 2), (2017, 3)]

def get_available_dates(root):
    # Testing - generate available_dates
    dates = []
    for f in root.iterdir():
        if f.is_dir() and f.name != 'csv':
            year, month = map(int, f.name.split("_"))
            dates.append((year, month))
    return dates

def get_word_folder(year, month, root):
    sub = str(year) + "_" + str(month).zfill(2)
    f = root / sub    
    if f.exists():
        return f.absolute()
    
def get_csv_folder(year, month, root):
    f = root / str(year) / str(month).zfill(2)    
    if f.exists():
        return f.absolute()  
    
    
def init_dirs(root, available_dates=available_dates):
    for d in available_dates:
        y, m = d
        f = root / str(y)
        sf = f / str(m).zfill(2) 
        for new_folder in [f, sf]:
            if not new_folder.exists():
               new_folder.mkdir()               

def accepted(path):
    if path.exists() and path.stat().st_size > 0:
        return True
    else:
        return False
    
def size(path):
    return int(round(path.stat().st_size / 1024, 0))
    
def as_str(y, m):      
    return str(y) + " " + str(m).zfill(2)

def echo(src, dest):
    print("    source:", src)
    print("    destination:", dest)

if __name__ == "__main__":
    import shutil
    import word
    
    WORD_ROOT = Path("D:/digital/kep_data2")
    # will fail when new month folder is added   
    assert set(available_dates)==set(get_available_dates(WORD_ROOT))

    INTERIM_ROOT = Path('C:/Users/PogrebnyakEV/Desktop/mini-kep-master/data/interim')
    #init_dirs(INTERIM_ROOT)
    
    for d in reversed(available_dates) :
        word_folder = get_word_folder(*d, WORD_ROOT)
        src = Path(word_folder) / "tab.csv"
        interim_folder = get_csv_folder(*d, INTERIM_ROOT )
        dest =  Path(interim_folder) / "tab.csv"
        # src and dest are present
        if accepted(src) and accepted(dest):
            s1 = size(src)              
            s2 = size(dest)
            # incompelte file copied
            if s1 > s2:
                shutil.copyfile(src, dest)
            assert s1 == s2
            print("Accepted", as_str(*d), s1, s2)
            echo(src, dest)         
        # not copied               
        if accepted(src) and not accepted(dest):
            shutil.copyfile(src, dest)
            print("Copied")
            echo(src, dest)                
        #     
        if not accepted(src):
            word.folder_to_csv(word_folder)
            shutil.copyfile(src, dest)
            print("Created and copied")
            pass
        
            
    # MAYDO: - zip/rar file archive on S3
    #        - download and unpack locally
    
    # MAYDO: - read from rosstat