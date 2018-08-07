"""Extract data from CSV file using parsing instructions."""

from kep.session.commands import get_instructions
from kep.session.dataframes import unpack_dataframes
from kep.parser import get_mapper, get_tables, Worker
from copy import copy


__all__ = ['Session']


class Session:
    def __init__(self, base_units_source: str, commands_source: str):
        """Initialise session with units of measurement and parsing instructions."""       
        self.base_mapper = get_mapper(base_units_source)
        self.command_blocks = get_instructions(commands_source)
        self.parsed_tables = []
        
    def parse(self, csv_source):
        """Extract data *csv_source*."""
        tables = get_tables(csv_source)
        self.parsed_tables = []
        _worker = Worker(tables, self.base_mapper)
        for block in self.command_blocks:
            worker = copy(_worker)
            next_tables = worker.apply_all(block.commands).parsed_tables
            worker.check_labels(block.expected_labels)
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
    
    def verify(self):
        pass