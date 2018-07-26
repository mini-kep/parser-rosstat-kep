from copy import copy
from kep.units import UnitMapper
from kep.util import iterate
from kep.reader import import_tables_from_string


class Worker:
    def __init__(self, tables, base_mapper: UnitMapper):
        self.tables = tables
        self.name = None
        self.base_mapper = base_mapper

    def start_with(self, start_strings):
        start_strings = iterate(start_strings)
        for i, t in enumerate(self.tables):
            if t.contains_any(start_strings):
                break
        self.tables = self.tables[i:]
        return self

    def end_with(self, end_strings):
        end_strings = iterate(end_strings)
        we_are_in_segment = True
        for i, t in enumerate(self.tables):
            if t.contains_any(end_strings):
                we_are_in_segment = False
            if not we_are_in_segment:
                break
        self.tables = self.tables[:i]
        return self

    def assign_units(self, unit):
        for t in self.tables:
            t.unit = unit
        return self

    def set_name(self, name):
        self.name = name

    def attach_headers(self, headers):
        headers = iterate(headers)
        for t in self.tables:
            if t.contains_any(headers):
                t.name = self.name
        return self

    def set_units(self, units):
        self.units = iterate(units)

    def parse_units(self):
        for i, t in enumerate(self.tables):
            for header in t.headers:
                unit = self.base_mapper.extract(header)
                if unit:
                    t.unit = unit

    def prev_next_pairs(self):
        return zip([None] + self.tables[:-1], self.tables)

    # TODO
    def trail_down_units(self):
        """Assign trailing variable names in tables.
           Trailing names are defined in leading table and pushed down
           to following tables, if their unit is specified in namers.units
        """
#        for prev_table, table in self.prev_next_pairs():
#            if (table.unit is None
#                and prev_table.unit is not None
#                and table.name):
#                table.unit = prev_table.unit
        pass

    def trail_down_names(self):
        """Assign trailing variable names in tables.
           Trailing names are defined in leading table and pushed down
           to following tables, if their unit is specified in namers.units
        """
        _units = copy(self.units)
        for i, table in enumerate(self.tables):
            if not _units:
                break
            if table.name and table.unit in _units:
                _units.remove(table.unit)
            if i >= 1 and table.name is None and table.unit in _units:
                table.name = self.tables[i - 1].name
                _units.remove(table.unit)

    # TODO
    def parse_units_with(self, mapper: dict={}):
        for t in self.tables:
            pass
        return self

    # TODO
    @property
    def labels(self):
        return [t.label for t in self.tables]

    # TODO
    def require(self, string):
        label, freq, date, value = string.split(' ')
        value = float(value)
        dp = row_model.Datapoint(label, freq, date, value)
        assert dp in self.datapoints


class Container:
    def __init__(self, csv_source: str, base_mapper: UnitMapper):
        self.incoming_tables = import_tables_from_string(csv_source)
        self.parsed_tables = []
        self.base_mapper = base_mapper
        self.worker = None

    def init(self):
        self.worker = Worker(self.incoming_tables, self.base_mapper)

    def apply(self, command_functions):
        self.init()
        for func in command_functions:
            func(self.worker)
        self.push()

    def check(self, expected_labels):
        if self.current_labels != expected_labels:
            raise AssertionError(self.current_labels, expected_labels)

    def push(self):
        current_parsed_tables = [t for t in self.worker.tables if t]
        self.parsed_tables.extend(current_parsed_tables)

    def require(self, string):
        label, freq, date, value = string.split(' ')
        value = float(value)
        dp = row_model.Datapoint(label, freq, date, value)
        assert dp in self.datapoints

    @property
    def datapoints(self):
        return list(self.emit_datapoints())

    def emit_datapoints(self):
        for t in self.parsed_tables:
            if t:
                for x in t.emit_datapoints():
                    yield x

    @property
    def labels(self):
        return [t.label for t in self.parsed_tables]

    @property
    def current_labels(self):
        return [t.label for t in self.worker.tables if t]