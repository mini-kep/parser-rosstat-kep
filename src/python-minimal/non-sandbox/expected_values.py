import pathlib
import yaml

import kep 

def get_checkpoints(path_csv):
    """Persisting checkpoints. Write first and last values
       of each time series to file 'checkpoints.yaml'.
    """
    expected_values = []
    for namer in kep.definition.NAMERS:
        param = path_csv, kep.definition.UNITS, [namer]
        tables = kep.reader.parsed_tables(*param)
        namer.assert_all_labels_found(tables)
        data = kep.reader.emit_datapoints(tables)
        print(namer.name)
        for label in namer.labels:
            print(label)
            subdata = [x for x in data if x['label'] == label]
            def one(i):
                x = subdata[i]
                expected_values.append(x)
                print(x)
            one(0)
            one(-1)
        return expected_values    


if __name__ == "__main__":
    from paths import PATH_CSV
    expected_values = get_checkpoints(PATH_CSV)
    pathlib.Path(PATH_CHECKPOINTS).write_text(yaml.dump(expected_values))