from pathlib import Path

from download import Downloader
from word2csv import folder_to_csv
from units import UNITS
from variables import YAML_DEFAULT, YAML_BY_SEGMENT 
from pipeline import create_parser
from to_dataframe.dataframe import create_dataframe

DATA_ROOT = Path(__file__).parents[1] / 'data' 
assert DATA_ROOT.exists()
                
class Locations():
    def __init__(self, year: int, month: int, data_root):
        self.year = year
        self.month = month
        self.data = Path(data_root) 
        
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
    def interim_csv(self):
        return self.inner_path('interim') / 'tab.csv' 

    def processed_csv(self, freq: str):
        return self.inner_path('processed')  / self.filename(freq) 

    def latest_csv(self, freq: str):
        return self.data / 'processed' / 'latest' / self.filename(freq) 
    
    @staticmethod
    def filename(freq):
        return 'df{}.csv'.format(freq)

# not used   
def make_reader(units=UNITS, 
                default_yaml=YAML_DEFAULT, 
                yaml_by_segment=YAML_BY_SEGMENT):
    return create_parser(units, default_yaml, yaml_by_segment)

def validate(df, freq):
    pass

def to_latest(year, month, data_root):
    pass

def is_latest(year, month):
    return True

def full(year,
         month, 
         units=UNITS, 
         default_yaml=YAML_DEFAULT, 
         yaml_by_segment=YAML_BY_SEGMENT,
         data_root=DATA_ROOT):
    loc = Locations(year, month, data_root)
    #perisist data
    d = Downloader(year, month, loc.raw_folder)
    d.download()
    d.unpack()
    if not loc.interim_csv.exists():
         folder_to_csv(loc.raw_folder, loc.interim_csv)
    #parse
    text = loc.interim_csv.read_text(encoding='utf-8')
    reader = create_parser(units, default_yaml, yaml_by_segment)
    values = list(reader(text))
    res = []
    # save dataframes
    for freq in 'aqm':
        df = create_dataframe(values, freq)
        res.append(df)        
        validate(df, freq)        
        df.to_csv(str(loc.processed_csv(freq)))
    if is_latest(year, month):
        to_latest(year, month, loc.data)
    return res  
        
if __name__ == '__main__':
    dfa, dfq, dfm = full(2018,4)

             