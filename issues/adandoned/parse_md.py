from pathlib import Path
from m2r import parse_from_file

# file locations
this = Path(__file__)
root_dir = this.parents[2]
src = 'concept.md'
dst = Path

# create 'readme.rst'
output = parse_from_file(src)
dst.write_text(output)
