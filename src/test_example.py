if __name__ == '__main__':
    from kep.helper.path import InterimCSV
    from kep.parsing_definition import PARSING_SPECIFICATION

    def tables(year, month, parsing_definition=PARSING_SPECIFICATION):
        csv_text = InterimCSV(year, month).text()
        return parsing_definition.attach_data(csv_text).tables

    tables = tables(2016, 10)
    e = Datapoints(tables)
    dfa = e.get_dataframe('a')
    dfq = e.get_dataframe('q')
    dfm = e.get_dataframe('m')

    from kep.csv2values.reader import text_to_rows
    from kep.csv2values.parser import extract_tables
    from kep.csv2values.specification import Definition

    # input data
    csv_segment = text_to_rows(
        """Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
1999	4823	901	1102	1373	1447
2000	7306	1527	1697	2038	2044""")

    # input instruction
    commands = dict(var="GDP", header="Объем ВВП", unit=["bln_rub"])
    pdef = Definition(commands, units={"млрд.рублей": "bln_rub"})

    # execution
    tables2 = extract_tables(csv_segment, pdef)
    e2 = Datapoints(tables2)
    dfa2 = e2.get_dataframe(freq='a')
    dfq2 = e2.get_dataframe(freq='q')
    dfm2 = e2.get_dataframe(freq='m')
