"""Extract data from CSV file using parsing instructions."""

from kep.reader import read_csv_from_file, split_to_tables, Table
from kep.parser import make_parser
from kep.units import UnitMapper
from kep.util import load_yaml
from kep.saver import unpack_dataframes


def read_command_blocks(source: str):
    return load_yaml(source)


def make_unit_mapper(source: str):
    units_dict = load_yaml(source)[0]
    return UnitMapper(units_dict)   



class Session:
    """Initialise session with units of measurement and parsing instructions
       Use parse() method to extract data from CSV file."""    
    def __init__(self, base_units_source: str, commands_source: str):
        self.base_mapper = make_unit_mapper(base_units_source)
        self.command_blocks = read_command_blocks(commands_source)
        self.parsed_tables = []
        
    def parse(self, csv_source):
        csv_rows = read_csv_from_file(csv_source)
        tables = [Table(h, d) for h, d in split_to_tables(csv_rows)]
        parser = make_parser(self.base_mapper)
        self.parsed_tables = []
        for commands in self.command_blocks:
            next_tables = parser(tables, commands)
            self.parsed_tables.extend(next_tables)

    @property
    def labels(self):
        return [t.label for t in self.parsed_tables]    

    def datapoints(self):
        return [x for t in self.parsed_tables for x in t.emit_datapoints()]
   
   
    def dataframes(self):
        dfa, dfq, dfm = unpack_dataframes(self.datapoints())
        return dfa, dfq, dfm