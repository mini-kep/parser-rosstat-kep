"""Extract data from CSV file using parsing instructions."""

from kep.reader import  get_tables
from kep.parser import make_parser
from kep.units import UnitMapper
from kep.util import load_yaml
from kep.saver import unpack_dataframes


def read_command_blocks(source: str):
    return load_yaml(source)


def get_parser(source: str):
    units_dict = load_yaml(source)[0]
    return make_parser(UnitMapper(units_dict))

class Session:
    """Initialise session with units of measurement and parsing instructions
       Use parse() method to extract data from CSV file."""    
    def __init__(self, base_units_source: str, commands_source: str):
        self.parser = get_parser(base_units_source)
        self.command_blocks = read_command_blocks(commands_source)
        self.parsed_tables = []
        
    def parse(self, csv_source):
        tables = get_tables(csv_source)
        self.parsed_tables = []
        for commands in self.command_blocks:
            next_tables = self.parser(tables, commands)
            self.parsed_tables.extend(next_tables)

    @property
    def labels(self):
        return [t.label for t in self.parsed_tables]    

    def datapoints(self):
        return [x for t in self.parsed_tables for x in t.emit_datapoints()]
   
   
    def dataframes(self):
        dfa, dfq, dfm = unpack_dataframes(self.datapoints())
        return dfa, dfq, dfm