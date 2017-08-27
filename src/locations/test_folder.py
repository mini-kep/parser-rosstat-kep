import pytest

from locations.folder import FolderBase as Folder

class Test_Folder():
    def test_repr(self):
        assert repr(Folder(2015, 5))

    def test_get_folder_methods(self):
        assert Folder(2015, 5).get_processed_folder().exists()
        assert Folder(2015, 5).get_interim_folder().exists()
        assert Folder(2015, 5).get_raw_folder().exists()
        assert Folder(2015, 5).get_interim_csv().exists()

    def test_out_of_range_year_does_not_raises_error(self):
        #with pytest.raises(ValueError):
            Folder(2030, 1)

# skipping

@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_md(folder):
    assert False

@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_copy_latest():
    assert False
    
   
if __name__ == "__main__":
    pytest.main([__file__])

