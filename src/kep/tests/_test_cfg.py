# -*- coding: utf-8 -*-
import pytest

import kep.spec as spec
import kep.tables as tables

#FIXME
# from .test_tables import Test_Function_get_year


# def marker_has_valid_start_and_end(marker):
    # """Helper function for marker validation."""

    # s = marker['start']
    # e = marker['end']

    # start_found = False
    # end_found = False

    # start_head = None
    # end_head = None

    # for head in Test_Function_get_year.all_heads():
        # if tables.is_year(head):
            # continue
        # if not start_found:
            # start_pos = head.find(s)
            # start_found = start_pos != -1
            # if start_found:
                # start_head = head
        # if start_found:
            # if not end_found:
                # end_pos = head.find(e)
                # end_found = end_pos != -1
                # if end_found:
                    # end_head = head

        # if start_found and end_found:
            # break

    # # start and end fields should come from different lines (heads), otherwise the condition should be changed
    # return start_found and end_found and (start_head != end_head)


def test_cfg_main_marker_valid():
    """Tests that main definition has only one marker specified and that its start and end fields are None."""

    markers = cfg.SPEC.main.scope.markers
    
    assert markers==[] #len(cfg.SPEC.main.markers) == 1

    #marker = cfg.SPEC.main.markers[0]
    #assert marker["start"] is None and marker["end"] is None


def test_cfg_additional_markers_valid():
    """Tests that all additional definitions markers are not None.
       Also tests that:
         * markers starts/ends are not None
         * each marker's start and end fields are located in a proper order in the latest CSV file, i.e.:
           start comes first, end comes second
    """
    pass

#    none_markers_notices = []
#    invalid_markers_notices = []
#
#    for pdef in cfg.SPEC.additional:
#        for marker in pdef.markers:
#            if marker["start"] is None or marker["end"] is None:
#                none_markers_notices.append("definition: '{}'; marker: '{}';".format(pdef, marker))
#
#    for pdef in cfg.SPEC.additional:
#        # for each definition take its first marker only
#        marker = pdef.markers[0]
#        if not marker_has_valid_start_and_end(marker):
#            invalid_markers_notices.append("definition: '{}'; marker not found: '{}'".format(pdef, marker))
#
#    if none_markers_notices or invalid_markers_notices:
#
#        if none_markers_notices:
#            print("markers with Nones:\n{}\n".format("-"*len("markers with Nones:")))
#            print("\n".join(none_markers_notices))
#
#        if invalid_markers_notices:
#            if none_markers_notices:
#                print("\n")
#
#            print("invalid markers:\n{}\n".format("-"*len("invalid markers:")))
#            print("\n".join(invalid_markers_notices))
#
#    assert (not none_markers_notices and not invalid_markers_notices) is True


if __name__ == "__main__":
    pytest.main([__file__])
