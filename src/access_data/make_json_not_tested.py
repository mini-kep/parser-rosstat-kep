# TODO: save to local cache, update cache


# json's
from pathlib import Path

# if in package, can import this from src.kep.cfg.py
FOLDER_LATEST_CSV = Path(__file__).parents[2] / "data" / "processed" / "latest"
FOLDER_LATEST_JSON = Path(__file__).parents[2] / "data" / "processed" / "json"


def json_path(freq, folder=FOLDER_LATEST_JSON):
    # FIXME: something nice than .__str__()
    return (folder / "df{}.json".format(freq)).__str__()


def csv_path(freq, folder=FOLDER_LATEST_CSV):
    return folder / "df{}.csv".format(freq)


def read_csv_safe_long_name(source):
    """Works safely on long directory names"""
    assert isinstance(source, Path)
    with source.open() as buf:
        return read_csv(buf)


def get_dfs():
    """Get three dataframes from local csv files"""
    dfa = read_csv_safe_long_name(csv_path('a'))
    dfq = read_csv_safe_long_name(csv_path('q'))
    dfm = read_csv_safe_long_name(csv_path('m'))
    return dfa, dfq, dfm


# IDEA: import local copy of "df*.csv" and update from web if necessary
#       see oil and CBR repositories for that


def save_json(folder_path):
    param = dict(orient="records")
    dfa, dfq, dfm = get_dfs()
    dfa.to_json(json_path('a'), **param)
    dfq.to_json(json_path('q'), **param)
    dfm.to_json(json_path('m'), **param)
    print("Saved dataframes as json to", folder_path)


if __name__ == "__main__":
    # FIXME: must quarantee 'latest' is updated
    dfa1, dfq1, dfm1 = get_dfs_from_web()
    dfa, dfq, dfm = get_dfs()

    # FIXME get_dfs_from_web() may be slow, otherwise could be a good test to
    # compare dfa1 to dfa, etc
    assert dfa1.equals(dfa)
    assert dfq1.equals(dfq)
    assert dfm1.equals(dfm)

    save_json(FOLDER_LATEST_JSON)
