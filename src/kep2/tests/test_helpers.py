# -*- coding: utf-8 -*-
import pytest
import kep2.helpers as files

year, month = files.get_latest_date()

# testing public methods
# __all__ = ['PathHelper', 'DateHelper']


#class PathHelper:
#    def locate_csv(year: int=None, month: int=None):
#        """Return interim CSV file based on *year* and *month*. Defaults to 
#           latest year and month.
#    
#           Returns:
#                pathlib.Path() instance
#        """
#        folder = Folder(year, month).get_interim_folder()
#        csv_path = folder / "tab.csv"
#        if csv_path.exists() and csv_path.stat().st_size > 0:
#            return csv_path
#        else:
#            raise FileNotFoundError(
#                "File not found or has zero length: {}".format(csv_path))
#
#    def get_processed_folder(year, month):
#        """Return processed CSV file folder based on *year* and *month*.
#    
#        The processed CSV file folder is used by Frames class
#        to write output files (dfa.csv, dfq.csv, dfm.csv).
#    
#        Returns:
#            pathlib.Path() instance
#    
#        """
#        return Folder(year, month).get_processed_folder()
#
#
#class DateHelper:
#    
#    def get_supported_dates():
#        return Folder.supported_dates        
#    
#    def get_latest_date():
#        """Return year and month for latest available interim data folder.
#    
#        Returns:
#            (year, month) tuple of two integers
#    
#        """
#        return Folder.get_latest_date()    
#        
#    def filter_date(year, month):
#        """Set (year, month) to latest date, even if year or month omitted.
#                    
#        Returns:
#            (year, month) tuple of two integers  
#        """
#        latest_year, latest_month = DateHelper.get_latest_date()
#        return year or latest_year, month or latest_month


class Test_PathHelper:
    
    def test_locate_csv_on_year_month_path_esists(self):
        assert files.locate_csv(year, month).exists() is True

    def test_locate_csv_on_noarg_works_and_retruns_path_that_esists(self):
        assert files.locate_csv().exists() is True

    def test_get_processed_folder_returns_existing_folder(self):
        assert files.get_processed_folder(year, month).exists() is True

    def test_get_processed_folder_will_not_work_without_arguments(self):
        with pytest.raises(TypeError):
            files.get_processed_folder()


class Test_DateHelper:
    
    def test_filled_dates_runs_on_Nones():
        assert files.filter_date(None, None) == files.get_latest_date() 
        
    def test_filled_dates_runs_on_Nones():    
        assert files.filter_date(2017, 5) == (2017, 5)
    
    def test_get_supported_dates_starts_in_2009_4():
        assert files.get_supported_dates()[0] == (2009, 4) 
            
    def test_get_latest_date():
        year, month = files.get_latest_date()
        assert year >= 2017
        assert month >= 1
        assert month <= 12


# more testing, 'private' part  

class Test_Folder():
    def test_repr(self):
        assert repr(files.Folder(2015, 5))

    def test_get_folder_methods(self):
        assert files.Folder(2015, 5).get_processed_folder().exists()
        assert files.Folder(2015, 5).get_interim_folder().exists()

    def test_out_of_range_year_raises_error(self):
        with pytest.raises(ValueError):
            files.Folder(2030, 1)
            
# skipping
            
@pytest.mark.skip(reason="not testing maintenance scripts yet")        
def test_md(folder):
    assert False    

@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_init_dirs():
    assert False
    
@pytest.mark.skip(reason="not testing maintenance scripts yet")
def test_copy_latest():
    assert False

if __name__ == "__main__":
    pytest.main([__file__])
    
    