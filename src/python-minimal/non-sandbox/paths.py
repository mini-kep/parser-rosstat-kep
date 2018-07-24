import pathlib

datafolder = pathlib.Path(__file__).parent / 'data'
PATH_CSV = str(datafolder / 'tab.csv')
PATH_CSV_LEGACY = str(datafolder / 'tab_old.csv')
PATH_CHECKPOINTS = str(datafolder / 'checkpoints.yaml')

