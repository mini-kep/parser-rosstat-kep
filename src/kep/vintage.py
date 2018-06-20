"""Extract dataframes by year and month.

Dataflow:    
   - csv data based on year and month + parsing definitions 
   - parsing jobs (job is a csv data block and its parsing definition) 
   - values 
   - dataframes by frequency

"""

from kep.helper.path import InterimCSV, ProcessedCSV, copy_to_latest
from kep.pipeline import create_parser, create_dataframe
from kep.parsing_definition import (DEFINITION_DEFAULT, DEFINITIONS_BY_SEGMENT, 
                                    verify)

class Vintage:
    def __init__(self, year: int, month: int):
        self.year, self.month = year, month
        self.values = self._values()     
        self.dfs = self._dataframes(self.values)
        self.validate()
        
    def _values(self):    
        csv_text = InterimCSV(self.year, self.month).text()
        parser = create_parser(DEFINITION_DEFAULT, DEFINITIONS_BY_SEGMENT)
        return list(parser(csv_text))
    
    @staticmethod
    def _dataframes(values):
        dfs = {}
        for freq in 'aqm':
            dfs[freq] = create_dataframe(values, freq) 
        return dfs

    def save(self):
        csv_processed = ProcessedCSV(self.year, self.month)
        for freq, df in self.dfs.items():
            path = csv_processed.path(freq)
            # Convert 1524.3999999999996 back to 1524.4
            # Deaccumulation procedure in extract_tables.py responsible
            # for float number generation. 
            # WONTFIX: the risk is loss of data for exchange rate, 
            #          may need fomatter by column. annual values can be
            #          a guidance for a number of decimal positions.
            df.to_csv(path, float_format='%.2f')
            print("Saved dataframe to", path)
            
    def validate(self):
        print('Started validation...')
        verify(**self.dfs) 
        print('All required checkpoints found in dataset, validation passed') 
            
    def to_latest(self):
        copy_to_latest(self.year, self.month) 

    #TODO: upload to a database
#    def upload(self):
#        from parsers.mover.uploader import Uploader
#        self.validate()
#        # FIXME: possible risk - *self.datapoints* may have different serialisation 
#        #        format compared to what Uploader() expects
#        #           (a) date format   
#        #           (b) extra keys in dictionary
#        Uploader(self.datapoints).post()          
            
    def __repr__(self):
        return "Vintage({}, {})".format(self.year, self.month)

if __name__ == "__main__": # pragma: no cover
    v = Vintage(2018, 4)    
    v.save()
    dfm = v.dfs['m']
    dfa = v.dfs['a']
    dfq = v.dfs['q']
    v.to_latest()
