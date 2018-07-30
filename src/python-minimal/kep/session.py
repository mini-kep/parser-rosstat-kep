"""Extract data from CSV file using parsing instructions and 
   units of measurement. 
"""

from kep.parser import Collector
from kep.units import UnitMapper
from kep.commands import CommandSet
from kep.interface import read, read_many
from kep.saver import unpack_dataframes


class Session:
    def __init__(self, base_units_source: str, commands_source: str):
        unit_dict = read(base_units_source)
        self.base_mapper = UnitMapper(unit_dict)
        self.command_blocks = read_many(commands_source)
        self.container = None

    def parse_tables(self, csv_source):
        container = Collector(csv_source, self.base_mapper)
        for commands in self.command_blocks:
            cs = CommandSet(commands)
            container.apply(cs.methods, cs.labels)
        self.container = container
    
    @property     
    def labels(self):
        return self.container.labels        
        
    def datapoints(self):
        return self.container.datapoints()
    
    def dataframes(self):
        dfa, dfq, dfm = unpack_dataframes(self.datapoints())
        return dfa, dfq, dfm
