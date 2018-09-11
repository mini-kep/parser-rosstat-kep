import kep


def run(year, month):
    # unpack: if file exists, do not download
    kep.download(year, month)
    # unpack: if word files exist, do not unpack
    kep.unpack(year, month)
    # rename: to_word
    kep.convert(year, month)
    kep.save_processed(year, month)
    kep.to_latest(year, month)
    kep.to_excel(year, month)


def save(year, month):
    kep.save_processed(year, month)
    kep.to_latest(year, month)
    kep.to_excel(year, month)


if __name__ == '__main__':
    year, month = 2018, 6
    dfa, dfq, dfm = kep.get_dataframes(year, month)
    