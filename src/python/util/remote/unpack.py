import os
import platform
from pathlib import Path
import subprocess

IS_WINDOWS = (platform.system() == 'Windows')

if IS_WINDOWS:
    UNRAR_EXE = str(Path(__file__).parent / 'bin' / 'UnRAR.exe')
else:
    UNRAR_EXE = 'unrar'


def unrar(filepath, folder, unrar_executable=UNRAR_EXE):
    # UnRAR wants its folder argument with '/'
    folder = "{}{}".format(folder, os.sep)
    tokens = [unrar_executable, 'e', str(filepath), folder, '-y']
    try:
        return subprocess.check_call(tokens)
    except subprocess.CalledProcessError as e:
        raise e


class DocFiles:
    def __init__(self, folder):
        self.folder = Path(folder)

    @property
    def paths(self):
        return [str(x) for x in self.folder.glob('*.doc*')]

    def exist(self):
        return len(self.paths) > 0

    def __str__(self):
        return ' ' * 4 + ('\n' + ' ' * 4).join(self.paths)


class Unpacker:
    def __init__(self, archive_filepath,
                 destination_folder):
        self.path = archive_filepath
        if not Path(self.path).exists():
            raise FileNotFoundError(self.path)
        self.folder = destination_folder
        self.status = (f'Already unpacked:\n{self.docs}'
                       if self.docs.exist()
                       else None)

    @property
    def docs(self):
        return DocFiles(self.folder)

    def run(self):
        res = unrar(self.path, self.folder)
        if res == 0:
            self.status = f'UnRARed {self.path}'
            return True
        return False
