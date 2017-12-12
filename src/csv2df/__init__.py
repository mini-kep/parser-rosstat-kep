"""Parses fuzzy CSV input and makes pandas dataframes.

An input may be a CSV like this:

::

      Объем ВВП, млрд.рублей / Gross domestic product, bln rubles
            год     1кв     2кв     3кв     4кв
      1999  4823    901     1102    1373    1447
      2000  7306    1527    1697    2038    2044

Such input will result in two dataframes, with annual and quarterly frequency:

::

              year  GDP_bln_rub
  1999-12-31  1999       4823.0
  2000-12-31  2000       7306.0


::

              year  qtr  GDP_bln_rub
  1999-03-31  1999    1        901.0
  1999-06-30  1999    2       1102.0
  1999-09-30  1999    3       1373.0
  1999-12-31  1999    4       1447.0
  2000-03-31  2000    1       1527.0
  2000-06-30  2000    2       1697.0
  2000-09-30  2000    3       2038.0
  2000-12-31  2000    4       2044.0

"""

__all__ = ['specification',
           'reader', 'parser',
           'util_label', 'util_row_splitter']

from . import (specification, reader, parser,
               util_label, util_row_splitter)
