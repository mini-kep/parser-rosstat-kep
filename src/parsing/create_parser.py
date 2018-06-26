from .extractor.extract_tables import evaluate_assignment
from .popper import yield_parsing_jobs
from .make_definitions import make_default_definition, make_segment_definition

def create_parser(units, default_yaml, yaml_by_segment):
    default_definition = make_default_definition(units, default_yaml)  
    other_definitions = make_segment_definition(units, yaml_by_segment)
    def _mapper(csv_text: str):
        jobs = yield_parsing_jobs(csv_text, default_definition, other_definitions) 
        for data, definition in jobs:
            for value in evaluate_assignment(data, definition):
                yield value
    return _mapper

