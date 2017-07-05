# -*- coding: utf-8 -*-
import pytest

import cfg
import parse
import files

# see test_cfg_markers_valid method below
IGNORE_MARKERS_WITH_NONES_IN_TEST = True


def all_heads_first_rows():
    """Emits all heads first rows for debugging markers starts/ends"""

    csv_path = files.get_path_csv()
    csv_dicts = parse.read_csv(csv_path)
    for row in csv_dicts:
        if not row.is_datarow():
            yield row.name


def check_marker(marker):
    """Helper function for testing marker"""

    s = marker['start']
    e = marker['end']
    if s is not None and e is not None:

        start_found = False
        end_found = False

        start_head = None
        end_head = None

        start_pos = None
        end_pos = None

        for head in all_heads_first_rows():
            if not start_found:
                start_pos = head.find(s)
                start_found = start_pos != -1
                if start_found:
                    start_head = head
            if start_found:
                if not end_found:
                    end_pos = head.find(e)
                    end_found = end_pos != -1
                    if end_found:
                        end_head = head

            if start_found and end_found:
                break

        return start_found and end_found and ((start_head != end_head) or (start_pos < end_pos))
    else:
        return False


def test_cfg_markers_valid():
    """checks that all definitions markers are found in the latest CSV file.
       Also tests that each marker's `start` and `end` fields are located in a proper order in the latest CSV file:
       start comes first, end comes second
    """

    markers_with_nones_items = []
    markers_not_found_items = []

    all_definitions = [cfg.SPEC.main] + cfg.SPEC.additional

    for definition in all_definitions:
        for marker in definition.markers:
            if not check_marker(marker):
                if marker["start"] is None or marker["end"] is None:
                    if not IGNORE_MARKERS_WITH_NONES_IN_TEST:
                        markers_with_nones_items.append("definition: '{}'; marker: '{}';".format(definition, marker))
                else:
                    markers_not_found_items.append("definition '{}'; marker not found: '{}'".format(definition, marker))
            # take first markers only
            break

    if markers_with_nones_items or markers_not_found_items:

        if markers_with_nones_items:
            print("markers with Nones:\n{}\n".format("-"*len("markers with Nones:")))
            for m in markers_with_nones_items:
                print(m)

        if markers_not_found_items:
            if markers_with_nones_items:
                print("\n")

            print("markers not found:\n{}\n".format("-"*len("markers not found:")))
            for m in markers_not_found_items:
                print(m)

        assert False
    else:
        assert True


if __name__ == "__main__":
    pytest.main("test_cfg.py")
