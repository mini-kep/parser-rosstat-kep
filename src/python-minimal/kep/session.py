"""Extract data from CSV file using parsing instructions."""

from kep.units import get_mapper
from kep.commands import read_instructions_for_headers
from kep.reader import get_tables
from kep.parser import make_parser
from kep.saver import unpack_dataframes


__all__ = ['Session']



class Session:
    def __init__(self, base_units_source: str, commands_source: str):
        """Initialise session with units of measurement and parsing instructions."""
        mapper = get_mapper(base_units_source)
        self.parser = make_parser(mapper)
        self.command_blocks = read_instructions_for_headers(commands_source)
        self.parsed_tables = []
        
    def parse(self, csv_source):
        """Extract data *csv_source*."""
        tables = get_tables(csv_source)
        self.parsed_tables = []
        for commands in self.command_blocks:
            next_tables = self.parser(tables, commands)
            self.parsed_tables.extend(next_tables)

    def labels(self):
        """Return list of labels from parsed tables."""
        return [t.label for t in self.parsed_tables]    

    def datapoints(self):
        """Return a list of values from parsed tables."""
        return [x for t in self.parsed_tables for x in t.emit_datapoints()]   
   
    def dataframes(self):
        """Return a tuple of annual, quarterly and monthly dataframes
           from parsed tables."""
        dfa, dfq, dfm = unpack_dataframes(self.datapoints())
        return dfa, dfq, dfm