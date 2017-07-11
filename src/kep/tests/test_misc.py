import pytest
import files

# regression tests - after bug fixes on occasional errors
def test_csv_has_no_null_byte():
    csv_path = files.get_path_csv(2015, 2)
    z = csv_path.read_text(encoding=files.ENC)
    assert "\0" not in z


if __name__ == "__main__":
    pytest.main([__file__])