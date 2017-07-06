REM Generates coverage results
coverage run --source=. -m pytest

REM From the results generates human readable report
coverage report -m --omit=test_*.py,tst_draft.py > coverage.output 

REM Make annotations
coverage annotate -d annotate

REM TODO: exclude test_*.py files from coverage commands
REM TODO: show coverage as online badge - what is the process to do it?