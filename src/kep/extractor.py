"""Extract dataframes."""
from kep.config import InterimCSV, FREQUENCIES
from kep.definitions.definitions import PARSING_DEFINITIONS
from kep.csv2df.reader import get_segment_with_pdef_from_text
from kep.csv2df.parser import extract_tables
from kep.csv2df.emitter import Emitter


def isin(checkpoints, df):   
     def is_found(df, d):
        dt = d['date']
        colname = d['name']
        x = d['value']
        try:
            return df.loc[dt, colname].iloc[0] == x
        except KeyError:
            return False
     return [is_found(df, c) for c in checkpoints]    


class Extractor:
    def __init__(self, text, parsing_definitions):
        self.text = text
        self.pdef_list = parsing_definitions
        self.dfs = self.get_dataframes(text, parsing_definitions)
        
    def get_dataframes(self, csv_text, parsing_definitions):
        # FIXME: maybe a parsing definition should contain a CSV text segment 
        #        that is a part from CSV text. CSV can be bound to pdef. 
        self.jobs = get_segment_with_pdef_from_text(csv_text, parsing_definitions)
        self.tables = [t for csv_segment, pdef in self.jobs
                         for t in extract_tables(csv_segment, pdef)]
        emitter = Emitter(self.tables)
        return {freq: emitter.get_dataframe(freq) for freq in FREQUENCIES}
        
    def isin(self, freq, checkpoints):        
        return isin(checkpoints, self.dfs[freq]) 
    
    def annual(self):
        return self.dfs['a']

    def quarterly(self):
        return self.dfs['q']

    def monthly(self):
        return self.dfs['m']

        
class Frame(Extractor):
    def __init__(self, year, month, parsing_definitions=PARSING_DEFINITIONS):
        text = InterimCSV(year, month).text()
        self.dfs = self.get_dataframes(text, parsing_definitions)
