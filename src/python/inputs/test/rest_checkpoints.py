import pytest
import pandas as pd


from inputs.checkpoints import (
    Annual,
    ValidationError,
    require,
    expect
)


@pytest.fixture(scope="module")
def dataframe():
    return pd.DataFrame.from_dict(
        {'AGROPROD_yoy': {pd.Timestamp('1999-12-31 00:00:00'): 103.8,
                          pd.Timestamp('2000-12-31 00:00:00'): 106.2}}
    )


@pytest.fixture(scope="module")
def absent():
    return [
        Annual(
            date="1999",
            label="some_really_long_test_variable",
            value=100.0,
        )
    ]


@pytest.fixture(scope="module")
def present():
    return [
        Annual(
            date="1999",
            label="AGROPROD_yoy",
            value=103.8,
        )
    ]


class Test_verify():

    def test_raises_value_error_on_missed_points(self, dataframe, absent):
        with pytest.raises(ValidationError):
            require(dataframe, absent)

    def test_returns_without_error_on_good_path(self, dataframe, present):
        require(dataframe, present)

    def test_expect_passed(self, dataframe, present, absent):
        expect(dataframe, present)
        expect(dataframe, absent)

# FIXME: will fail on longer datasets

#dispatch.get_dataframe(2017, 1, 'a').columns
# Out[30]:
# Index(['year', 'CPI_ALCOHOL_rog', 'CPI_FOOD_rog', 'CPI_NONFOOD_rog',
#       'CPI_SERVICES_rog', 'CPI_rog', 'EXPORT_GOODS_bln_usd', 'GDP_bln_rub',
#       'GDP_yoy', 'GOV_EXPENSE_CONSOLIDATED_bln_rub',
#       'GOV_EXPENSE_FEDERAL_bln_rub', 'GOV_EXPENSE_SUBFEDERAL_bln_rub',
#       'GOV_REVENUE_CONSOLIDATED_bln_rub', 'GOV_REVENUE_FEDERAL_bln_rub',
#       'GOV_REVENUE_SUBFEDERAL_bln_rub', 'GOV_SURPLUS_FEDERAL_bln_rub',
#       'GOV_SURPLUS_SUBFEDERAL_bln_rub', 'IMPORT_GOODS_bln_usd', 'INDPRO_yoy',
#       'INVESTMENT_bln_rub', 'INVESTMENT_yoy', 'RETAIL_SALES_FOOD_bln_rub',
#       'RETAIL_SALES_FOOD_yoy', 'RETAIL_SALES_NONFOOD_bln_rub',
#       'RETAIL_SALES_NONFOOD_yoy', 'RETAIL_SALES_bln_rub', 'RETAIL_SALES_yoy',
#       'TRANSPORT_FREIGHT_bln_tkm', 'UNEMPL_pct', 'WAGE_NOMINAL_rub',
#       'WAGE_REAL_yoy'],
#      dtype='object')


if __name__ == "__main__":
    pytest.main([__file__])
