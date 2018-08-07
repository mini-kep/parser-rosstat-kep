import os
import platform
from pathlib import Path
import subprocess

__all__ = ['unpack']

IS_WINDOWS = platform.system() == 'Windows'
UNRAR_EXE = (str(Path(__file__).parent / 'bin' / 'UnRAR.exe')
             if IS_WINDOWS
             else 'unrar')


def _unrar(filepath: str, folder: str, unrar_executable=UNRAR_EXE):
    """Unpack *filepath* to *folder*."""
    # UnRAR wants its folder argument with '/'
    folder = "{}{}".format(folder, os.sep)
    tokens = [unrar_executable, 'e', str(filepath), folder, '-y']
    try:
        return subprocess.check_call(tokens)
    except subprocess.CalledProcessError as e:
        raise e


def unpack(filepath, destination_folder, force=False):
    assert_exists(filepath)
    assert_exists(destination_folder)
    docs = docs_listing(destination_folder)
    if docs and not force:
        return "Already unpacked: %r" % docs
    res = _unrar(filepath, destination_folder)
    if res == 0:
        return "UnRARed to %s" % destination_folder
    return 'UnRAR failed with code %s' % res


def assert_exists(filepath):
    if not Path(filepath).exists():
        raise FileNotFoundError(filepath)


def docs_listing(folder):
    return [str(x) for x in Path(folder).glob('*.doc*')]
