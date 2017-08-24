import pytest
from kep.helpers import PathHelper

# regression tests - after bug fixes on occasional errors


def test_csv_has_no_null_byte():
    csv_path = PathHelper.locate_csv(2015, 2)
    z = csv_path.read_text(encoding='utf-8')
    assert "\0" not in z


if __name__ == "__main__":
    pytest.main([__file__])
