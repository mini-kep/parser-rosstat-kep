import os
import platform
from pathlib import Path
import subprocess

IS_WINDOWS = (platform.system() == 'Windows')

if IS_WINDOWS:
    UNRAR_EXE = str(Path(__file__).parent / 'bin' / 'UnRAR.exe')
else:
    UNRAR_EXE = 'unrar'


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
                 destination_folder,
                 unrar_executable=UNRAR_EXE):
        if not Path(archive_filepath).exists():
            raise FileNotFoundError(archive_filepath)
        self.path = archive_filepath
        self.folder = destination_folder
        self.unrar_executable = unrar_executable
        self.status = (f'Already unpacked:\n{self.docs}'
                       if self.docs.exist()
                       else None)

    @property
    def docs(self):
        return DocFiles(self.folder)

    @property
    def tokens(self):
        # UnRAR wants its folder argument with '/'
        folder = "{}{}".format(self.folder, os.sep)
        return [str(self.unrar_executable), 'e', str(self.path), folder, '-y']

    def _call(self):
        try:
            return subprocess.check_call(self.tokens)
        except subprocess.CalledProcessError as e:
            self.status = 'Cannot execute:' + ' '.join(self.tokens)
            raise e

    def run(self):
        res = self._call()
        if res == 0:
            self.status = f'UnRARed {self.path}'
            return True
        return False
