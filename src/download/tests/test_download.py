import pytest
import tempfile
from pathlib import Path

from ..download import Downloader, Unpacker


class Test_Downloader_and_Unpacker():

    def setup_method(self):
        self.path = Path(tempfile.tempdir) / '123.rar'
        self.d = Downloader(2016, 12, self.path)
        self.res = self.d.run()

    def teardown_method(self):
        self.path.unlink()

    def test_Downloader_run_method_returns_True(self):
        assert self.res is True
        assert self.d.path.exists()
        assert isinstance(self.d.status, str)

    def test_Unpacker_run_method_returns_True(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            u = Unpacker(self.path, tmpdir)
            res = u.run()
            assert res is True
            assert u.docs.exist()
            assert isinstance(u.status, str)

    def test_Downloader_check_date_negative(self):
        with pytest.raises(ValueError):
            _ = Downloader(2016, 11, self.path)
