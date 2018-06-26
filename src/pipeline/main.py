from .this_parser.extract_tables import evaluate_assignment
from .reader.boundaries import get_boundaries
from .reader.popper import Popper
from .make_definitions import make_default_definition, make_segment_definition

def yield_parsing_jobs(csv_text: str, definition_default, definitions_by_segment):
    stack = Popper(csv_text)
    for pdef in definitions_by_segment:
        start, end = get_boundaries(pdef.boundaries, stack.rows)
        yield stack.pop(start, end), pdef
    yield stack.remaining_rows(), definition_default

def create_parser(units, default_yaml, yaml_by_segment):
    default_definition = make_default_definition(units, default_yaml)  
    other_definitions = make_segment_definition(units, yaml_by_segment)
    def _mapper(csv_text: str):
        jobs = yield_parsing_jobs(csv_text, default_definition, other_definitions) 
        for data, definition in jobs:
            for value in evaluate_assignment(data, definition):
                yield value
    return _mapper

