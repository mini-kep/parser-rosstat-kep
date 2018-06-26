"""Run full cycle of data processing from download to saving dataframe."""

# Workflow
# --------    
#
# 1. what is latest date available? 
# 2. could newer data have come already?
# 3. [+] let's parse the new data 
# 4. [-] commit to repo
# 5. upload to database
# 6. create a PDF handout or other assets

# Something to know:
# ------------------ 
# - output: 
#   - industrial production and other busness activity
#   - corp profits
# - housing construction
# - retail sales and household incomes    
# - budget expenditure and revenues
# - export and import
# - prices, inflation, interest rates
# - exchange rate
# - Q:GDP
# - Q:investment (unrelaible)
# - targets/forecasts   


from pathlib import Path
import shutil

from download import Downloader, Unpacker
from word2csv import folder_to_csv
from units import UNITS
from variables import YAML_DEFAULT, YAML_BY_SEGMENT 
from parsing import create_parser
from dataframe import create_dataframe
from checkpoints import verify 
from util import is_latest, save_excel


FREQUENCIES = list('aqm')
PROJECT_ROOT = Path(__file__).parents[1]
DATA_ROOT = PROJECT_ROOT / 'data' 
OUTPUT_ROOT = PROJECT_ROOT / 'output' 
assert DATA_ROOT.exists()
assert OUTPUT_ROOT.exists()
                
class Locations():
    def __init__(self, year: int, 
                 month: int, 
                 data_root,
                 output_root):
        self.year = year
        self.month = month
        self.data = Path(data_root) 
        self.out = Path(output_root) 
        
    def inner_path(self, tag):    
        if not tag in ('raw', 'interim', 'processed'):
            raise ValueError(tag)
        folder = self.data / tag / str(self.year) / str(self.month).zfill(2)
        if not folder.exists():
             folder.mkdir(parents=True)
        return folder            
    
    @property
    def raw_folder(self):
        return self.inner_path('raw')

    @property
    def archive_filepath(self):
        return str(self.raw_folder / 'download.rar')

    @property
    def interim_csv(self):
        return self.inner_path('interim') / 'tab.csv' 

    def processed_csv(self, freq: str):
        return self.inner_path('processed')  / self.filename(freq) 

    def latest_csv(self, freq: str):
        return self.data / 'processed' / 'latest' / self.filename(freq) 
    
    @staticmethod
    def filename(freq):
        return 'df{}.csv'.format(freq)
    
    @property
    def xlsx_filepath(self):
        return str(self.out / 'kep.xlsx')

# not used   
def make_reader(units=UNITS, 
                default_yaml=YAML_DEFAULT, 
                yaml_by_segment=YAML_BY_SEGMENT):
    return create_parser(units, default_yaml, yaml_by_segment)

def to_latest(year:int, month: int, loc):
     """Copy csv files from folder like *processed/2017/04* to 
        *processed/latest*.
     """    
     for freq in FREQUENCIES:    
         src = loc.processed_csv(freq)
         dst = loc.latest_csv(freq)      
         shutil.copyfile(str(src), str(dst))
         print("Updated", dst)
     print(f"Latest folder now refers to {loc.year}-{loc.month}")

def to_excel(path, dfs):
    save_excel(path, dfs)   
    print('Saved Excel file to:\n    ', path)

def update(year,
         month, 
         units=UNITS, 
         default_yaml=YAML_DEFAULT, 
         yaml_by_segment=YAML_BY_SEGMENT,
         data_root=DATA_ROOT,
         output_root=OUTPUT_ROOT,
         force=False):
    # filesystem
    loc = Locations(year, month, data_root, output_root)
    # perisist data
    d = Downloader(year, month, loc.archive_filepath)
    d.download(force)
    u = Unpacker(loc.archive_filepath, loc.raw_folder)
    u.unpack(force)
    # convert Word to csv
    if force or not loc.interim_csv.exists():
         folder_to_csv(loc.raw_folder, loc.interim_csv)
    # parse
    text = loc.interim_csv.read_text(encoding='utf-8')
    parse = create_parser(units, default_yaml, yaml_by_segment)
    values = list(parse(text))
    # save dataframes
    dfs = {}
    for freq in 'aqm':
        df = create_dataframe(values, freq)
        dfs[freq] = df
        verify(df, freq)        
        df.to_csv(str(loc.processed_csv(freq)))
    if is_latest(year, month):
        to_latest(year, month, loc)
        to_excel(loc.xlsx_filepath, dfs)        

    return dfs  
        
if __name__ == '__main__':
    dfs = update(2018, 4)
    dfa, dfq, dfm = (dfs[freq] for freq in FREQUENCIES)

             