"""Helper functions."""
import pathlib
import tempfile
import os


class TempFile():
    def __init__(self, content: str, encoding='utf-8'):
        with tempfile.NamedTemporaryFile() as f:
            self.path = f.name
        self.obj = pathlib.Path(self.path)
        self.obj.write_text(content, encoding)

    def __enter__(self):
        return self.path

    def __exit__(self, *args):
        self.obj.unlink()


def exists(filename):
    try:
        return os.path.exists(filename)
    except ValueError:
        return False
