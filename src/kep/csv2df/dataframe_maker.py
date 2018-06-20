"""Creating pandas dataframes."""

import pandas as pd


def get_duplicates(df):
    if df.empty:
        return df
    else:
        return df[df.duplicated(keep=False)]


def check_duplicates(df):
    if df.empty:
        dups = df
    else:
        dups = df[df.duplicated(keep=False)]
    if not dups.empty:
        # raise ValueError("Duplicate rows found {}".format(dups))
        print("Duplicate rows found {}".format(dups))


def create_dataframe(datapoints, freq):    
    df = pd.DataFrame([x for x in datapoints if x['freq'] == freq])
    if df.empty:
        return pd.DataFrame()
    #import pdb; pdb.set_trace()
    check_duplicates(df)
    df = df.drop_duplicates(['freq', 'label', 'time_index'], keep='first')
    # reshape
    df = df.pivot(columns='label', values='value', index='time_index')
    # delete some internals for better view
    df.columns.name = None
    df.index.name = None
    # add year
    df.insert(0, "year", df.index.year)
    # add period
    if freq == "q":
        df.insert(1, "qtr", df.index.quarter)
    if freq == "m":
        df.insert(1, "month", df.index.month)
    # transform variables:
    if freq == "a":
        df = rename_accum(df)
    if freq == "q":
        df = deaccumulate(df, first_month=3)
    if freq == "m":
        df = deaccumulate(df, first_month=1)
    return df        

# government revenue and expense time series transformation


def rename_accum(df):
    return df.rename(mapper=lambda s: s.replace('_ACCUM', ''), axis=1)


def deacc_main(df, first_month):
    # save start of year values
    original_start_year_values = df[df.index.month == first_month].copy()
    # take a difference
    df = df.diff()
    # write back start of year values (January in monthly data, March in qtr
    # data)
    ix = original_start_year_values.index
    df.loc[ix, :] = original_start_year_values
    return df


def deaccumulate(df, first_month):
    varnames = [
        vn for vn in df.columns if vn.startswith('GOV') and (
            "ACCUM" in vn)]
    df[varnames] = deacc_main(df[varnames], first_month)
    return rename_accum(df)


if __name__ == '__main__':  # pragma: no cover
    from kep.helper.path import InterimCSV
    from kep.parsing_definition import PARSING_SPECIFICATION

    def values(year, month, parsing_spec=PARSING_SPECIFICATION):
        csv_text = InterimCSV(year, month).text()
        parsing_spec.attach_data(csv_text)
        return parsing_spec.values                                

    values = values(2016, 10)
    dfa = create_dataframe(values, 'a')
    dfq = create_dataframe(values, 'q')
    dfm = create_dataframe(values, 'm')

    from kep.csv2df.reader import text_to_list
    from kep.csv2df.parser import Segment
    from kep.csv2df.specification import Definition

    # input data
    csv_segment = text_to_list(
        """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")

    # input instruction
    commands = dict(var="GDP", header="Объем ВВП", unit=["bln_rub"])
    pdef = Definition(commands, units={"млрд.рублей": "bln_rub"})

    # execution
    seg = Segment(csv_segment, pdef)
    values = seg.values
    dfa2 = create_dataframe(values, freq='a')
    dfq2 = create_dataframe(values, freq='q')
    dfm2 = create_dataframe(values, freq='m')
