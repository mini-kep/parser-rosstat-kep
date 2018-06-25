# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 23:53:17 2018

@author: Евгений
"""

class FileLocations():
    def __init__(self, root: str, year, month):
        self.root = Path(root)
        data = self.root / 'data' 
        self.raw = data / 'raw'
        self.interim = data / 'interim'
        self.processed = data / 'processed'
        self.latest = self.processed / 'latest'
        self.year = year
        self.month = month
    
    def raw_folder(self):
        pass

    def interim_csv(self):
        pass

    def processed_csv(self,freq: str):
        pass



def download(year, month, folder):
    pass

def unpack(year, month, folder):
    pass

def word2csv(source_folder, interim_csv_path):
    pass

def get_text(csv_path: str):
    pass

def extract_values(text: str, variables: dict, units: dict):
    pass

def as_dataframe(values, freq):
    pass

def to_csv(df, csv_path):
    pass

from pathlib import Path
ROOT=Path(__file__).parents[1]

def main(year, month, variables, units, root=ROOT):
    locations = FileLocations(root, year, month) 
    download(year, month, locations.raw_folder())
    unpack(year, month, locations.raw_folder())
    word2csv(locations.raw_folder(), locations.interim_csv())
    text = get_text(locations.interim_csv())
    values = list(extract_values(text, variables, units))
    for freq in 'aqm':
        to_csv(df = as_dataframe(values, freq),
                csv_path = locations.processed_csv(freq)) 