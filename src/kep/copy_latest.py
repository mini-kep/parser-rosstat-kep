# TODO: this is a separate functionality - desired behaviour is copying all files from latest porcessed folder 

import shutil

import kep.config as config


def get_latest_date(base_dir):
    """Return (year, month) tuple corresponding to
       latest filled subfolder of *base_dir*.
    """
    def max_subdir(folder):
        subfolders = [f.name for f in folder.iterdir() if f.is_dir()]
        return max(map(int, subfolders))
    year = max_subdir(base_dir)
    month = max_subdir(base_dir / str(year))
    return year, month

# latest date found in interm data folder
LATEST_DATE = get_latest_date(config.Folders.interim)


# class Latest:
#     url = ('https://raw.githubusercontent.com/mini-kep/parser-rosstat-kep/'
#            'master/data/processed/latest')

#     def csv(freq):
#         return Folders.latest / ProcessedCSV.make_filename(freq)

# FIXME: vulnerable to proper date, attempts working in empty directory

# def copy_latest():
#     """Copy csv files from folder like
#            *processed/2017/04*
#        to
#            *processed/latest* folder.
#     """
#     year, month = LATEST_DATE
#     csv_file = config.ProcessedCSV(year, month)

#     # ERROR: will not work here
#     latest = config.Latest
#     for freq in config.FREQUENCIES:
#         src = csv_file.path(freq)
#         dst = latest.csv(freq)
#         shutil.copyfile(src, dst)
#         print('Copied', src)


# class Test_Latest():
#     def test_csv_method_returns_existing_files(self):
#         for freq in 'aqm':
#             Latest_csv = Latest.csv(freq)
#             assert Latest_csv.exists()

#     def test_csv_method_returns_df_a_q_m_csv(self):
#         for freq in 'aqm':
#             expected_name = 'df{}.csv'.format(freq)
#             Latest_csv = Latest.csv(freq)
#             assert Latest_csv.name == expected_name
