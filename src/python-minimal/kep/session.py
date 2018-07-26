"""Extract data from CSV file using parsing instructions and 
   units of measurement. 
"""

from kep.parser import Container
from kep.units import UnitMapper
from kep.commands import CommandSet
from kep.interface import read, read_many


class Session:
    def __init__(self, base_units_source: str, commands_source: str):
        unit_dict = read(base_units_source)
        self.base_mapper = UnitMapper(unit_dict)
        self.command_blocks = read_many(commands_source)

    def parse_tables(self, csv_source):
        container = Container(csv_source, self.base_mapper)
        for commands in self.command_blocks:
            cs = CommandSet(commands)
            container.apply(cs.methods)
            container.check(cs.labels)
        return container
