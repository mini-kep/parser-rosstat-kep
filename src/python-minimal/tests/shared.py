import pathlib
import tempfile    

class TempFile():
    def __init__(self, content: str):
        with tempfile.NamedTemporaryFile() as f:
            self.path = f.name        
        self.obj = pathlib.Path(self.path)
        self.obj.write_text(content, encoding='utf-8')

    def __enter__(self):
        return self.path 

    def __exit__(self, *args):
        self.obj.unlink()