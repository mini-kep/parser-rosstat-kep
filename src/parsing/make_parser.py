from parsing.csv_reader import clean_rows, read_csv, pop_rows
from parsing.definition import create_definitions
from parsing.extract import evaluate_assignment


def create_parser(units, default_yaml, yaml_by_segment):
    # read yamls
    default_definition = create_definitions(units, default_yaml)[0]
    other_definitions = create_definitions(units, yaml_by_segment)
    # bundle to parser

    def _mapper(csv_text: str):
        jobs = yield_parsing_jobs(
            csv_text,
            default_definition,
            other_definitions)
        for csv_rows, definition in jobs:
            for value in evaluate_assignment(csv_rows, definition):
                yield value
    return _mapper


def yield_parsing_jobs(
        csv_text: str,
        definition_default,
        definitions_by_segment):
    csv_rows = clean_rows(read_csv(csv_text))
    for current_definition in definitions_by_segment:
        start, end = current_definition.select_applicable_boundaries(csv_rows)
        csv_segment = pop_rows(csv_rows, start, end)
        yield csv_segment, current_definition
    yield csv_rows, definition_default
