"""
Extract data from CSV file using parsing instructions and units of measurement. 

Inputs
======
    - CSV file (as sandbox.CSV_TEXT)
    - parsing instructions (as sandbox.INTRUCTIONS_DOC)
    - default units of measurement (as sandbox.UNITS_DOC)

Output
======
    - list of parsed tables 
    - each parsed table is assigned with variable name, unit of measirement 
      and row format
    - method to extract data from table
    
Pseudocode
==========

1. split incoming CSV file to tables
2. repeat for all given parsing instruction: 
    a. establish block of tables
        - either all tables in CSV file,  
        - or a subset of tables, if start and end text lines are provided
    b. apply parsing instructions to block of tables
    c. check expected variable names and units of measurement 
       are found in block of tables
    d. save parsed tables to queue
3. emit datapoints from queue of parsed tables
4. check values in from parsed tables (not implemented, todo)

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
