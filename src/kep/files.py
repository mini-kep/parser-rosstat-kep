from pathlib import Path
import shutil 

# csv file parameters
ENC = 'utf8'
CSV_FORMAT = dict(delimiter='\t', lineterminator='\n')


#FIXME: hardcoded constant will not update to new months
DATES =     [                                 (2009, 4), (2009, 5), (2009, 6), 
             (2009, 7), (2009, 8), (2009, 9), (2009, 10), (2009, 11), (2009, 12), 
             
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
             
             (2017, 1), (2017, 2), (2017, 3), (2017, 4)]

def filled_dates(available_dates=DATES):
    for date in reversed(available_dates): 
        csv_path = get_path_csv(*date) 
        if csv_path.exists() and csv_path.stat().st_size > 0:
            yield date

def filter_date(year, month):
    if not year and not month:
        year, month = InterimDataFolder().get_latest_date()
        return year, month
    elif (year, month) in list(filled_dates()):
        return year, month
    else:
        raise ValueError("Date not found: {} {}".format(year, month))

# TODO - accoutn for latest in folder structure
"""
\data
  \raw      
      \2017
      \...
  \interim
      \2017
      \...          
  \processed
      \latest
      \latest_json
      \vintages
      \2017
      \...
"""
# we are in src/kep
levels_up = 2
data_folder = Path(__file__).parents[levels_up] / 'data' 
rosstat_folder = data_folder / 'interim'
processed = data_folder / 'processed'
latest = processed / 'latest'
latest_json = processed / 'latest_json'

def init_dirs(root, available_dates=DATES):
    for d in available_dates:
        y, m = d
        f = root / str(y)
        sf = f / str(m).zfill(2) 
        for new_folder in [f, sf]:
            if not new_folder.exists():
               new_folder.mkdir() 


class InterimDataFolder():
    """Find latest month available in interim data folder"""
    
    @staticmethod
    def list_subfolders(folder):
        return [f.name for f in folder.iterdir() if f.is_dir()]
    
    def __init__(self, folder=rosstat_folder):
        self.folder = folder
        assert self.get_latest_date() == DATES[-1]

    def max_year(self):
        return max(self.list_subfolders(self.folder))
        
    def max_month(self):
        subfolder = self.folder / self.max_year()
        return max(self.list_subfolders(subfolder))
    
    def get_latest_date(self):
        return int(self.max_year()), int(self.max_month())
    
    def get_latest_folder(self):
        year, month = self.get_latest_date()
        return __loc__(year, month, root=self.folder)

    
def __loc__(year, month, root):
    if not year and not month:
        year, month = InterimDataFolder().get_latest_date()    
    if year and month:
        month_dir = str(month).zfill(2)
        return root / str(year) / month_dir 


def get_path_csv(year=None, month=None):
    """Return interim CSV file path based on year and month"""
    return __loc__(year, month, root=rosstat_folder) / 'tab.csv'


def get_processed_folder(year=None, month=None):  
    """Return processed CSV file path based on year and month"""
    return __loc__(year, month, root=processed)


def copy_latest_csv_to_separate_folder(dst_folder=latest):
    # copy all files from folder like 2017/4 to 'latest'
    year, month = InterimDataFolder().get_latest_date()
    src_folder = get_processed_folder(year, month) 
    for src in [f for f in src_folder.iterdir() if f.is_file()]:
        dst = dst_folder / src.name
        shutil.copyfile(src, dst)      


if __name__ == "__main__":
    init_dirs(processed)
    init_dirs(rosstat_folder)
    copy_latest_csv_to_separate_folder()