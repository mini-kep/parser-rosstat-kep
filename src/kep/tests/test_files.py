# -*- coding: utf-8 -*-
import pytest
import kep.files as files

year, month = files.get_latest_date()

class Test_get_latest_date():    
    def test_():        
        year, month = files.get_latest_date()
        assert year >= 2017
        assert month >= 1
        assert month <= 12

class Test_locate_csv():    

    def test_1():
        assert files.locate_csv().exists() is True

    def test_2():    
        assert files.locate_csv(year, month).exists() is True


class Test_get_processed_folder():
   def test_retruns_existing_folder():
       assert files.get_processed_folder(year, month).exists() is True
                                     
   def test_will_not_work_without_arguments():                                      
       with pytest.raises(TypeError):
           files.get_processed_folder()
                                     
class Test_Folder():
    
    def test_repr():
        assert repr(files.Folder(2015, 5))
    
    def test_get_folder_methods():
        assert files.Folder(2015, 5).get_processed_folder().exists()
        assert files.Folder(2015, 5).get_interim_folder().exists()

    def test_out_ofrange_year_raises_error():
        with pytest.raises(ValueError):
            files.Folder(2030, 1)

if __name__ == "__main__":
    pytest.main()
