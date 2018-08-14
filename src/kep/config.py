from pathlib import Path

__all__ = ['DATA_ROOT', 'OUTPUT_ROOT']

_LEVELS_UP = 2
_PROJECT_ROOT = Path(__file__).parents[_LEVELS_UP]


DATA_ROOT = _PROJECT_ROOT / 'data'
OUTPUT_ROOT = _PROJECT_ROOT / 'output'
assert DATA_ROOT.exists()
assert OUTPUT_ROOT.exists()
