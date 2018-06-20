"""Create units of work that contain data and parsing parameters.

    yield_parsing_assingments(...)

"""
from kep.pipeline.parser.extract_tables import evaluate_assignment
from kep.pipeline.reader.boundaries import get_boundaries
from kep.pipeline.reader.popper import Popper


def yield_parsing_jobs(csv_text: str, definition_default, definitions_by_segment):
    stack = Popper(csv_text)
    for pdef in definitions_by_segment:
        start, end = get_boundaries(pdef.boundaries, stack.rows)
        yield stack.pop(start, end), pdef
    yield stack.remaining_rows(), definition_default


def create_parser(default_definition, other_definitions):
    def _mapper(csv_text: str):
        jobs = yield_parsing_jobs(csv_text, default_definition, other_definitions) 
        for data, definition in jobs:
            for value in evaluate_assignment(data, definition):
                yield value
    return _mapper

