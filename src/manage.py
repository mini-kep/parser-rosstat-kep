import kep


def run(year, month):
    kep.download(year, month)
    kep.unpack(year, month)
    kep.convert(year, month)
    kep.save_processed(year, month)
    kep.to_latest(year, month)
    kep.to_excel(year, month)


if __name__ == '__main__':
    year, month = 2018, 6
    dfa, dfq, dfm = kep.get_dataframes(year, month)
