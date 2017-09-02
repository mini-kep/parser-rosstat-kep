# -*- coding: utf-8 -*-
import pandas as pd
from io import StringIO
import functools


def to_dataframe(text):
    return pd.read_csv(StringIO(text), sep="\t",
                       converters={0: pd.to_datetime},
                       index_col=0)


dfa_text = """	year	CPI_ALCOHOL_rog	CPI_FOOD_rog	CPI_NONFOOD_rog	CPI_SERVICES_rog	CPI_rog	EXPORT_GOODS_bln_usd	GDP_bln_rub	GDP_yoy	GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub	GOV_EXPENSE_ACCUM_FEDERAL_bln_rub	GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub	GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub	GOV_REVENUE_ACCUM_FEDERAL_bln_rub	GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub	GOV_SURPLUS_ACCUM_FEDERAL_bln_rub	GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub	IMPORT_GOODS_bln_usd	INDPRO_yoy	INVESTMENT_bln_rub	INVESTMENT_yoy	RETAIL_SALES_FOOD_bln_rub	RETAIL_SALES_FOOD_yoy	RETAIL_SALES_NONFOOD_bln_rub	RETAIL_SALES_NONFOOD_yoy	RETAIL_SALES_bln_rub	RETAIL_SALES_yoy	TRANSPORT_FREIGHT_bln_tkm	UNEMPL_pct	WAGE_NOMINAL_rub	WAGE_REAL_yoy
1999-12-31	1999	143.2	135.0	139.2	134.0	136.5	75.6	4823.0	106.4	1258.0	666.9	653.8	1213.6	615.5	660.8	-51.4	7.0	39.5		670.4	105.3	866.1	93.6	931.3	94.7	1797.4	94.2	3372.0	13.0	1523.0	78.0
2000-12-31	2000	125.0	117.1	118.5	133.7	120.2	105.0	7306.0	110.0	1960.1	1029.2	1032.1	2097.7	1132.1	1065.8	102.9	33.8	44.9		1165.2	117.4	1093.2	107.5	1259.1	110.5	2352.3	109.0	3542.0	10.5	2223.0	120.9
2001-12-31	2001	112.6	117.8	112.7	136.9	118.6	101.9	8944.0	105.1	2419.4	1321.9	1330.2	2683.7	1594.0	1322.4	272.1	-7.8	53.8		1504.7	111.7	1416.8	107.6	1653.2	113.9	3070.0	111.0	3651.0	9.0	3240.0	119.9
2002-12-31	2002	108.9	111.3	110.9	136.2	115.1	107.3	10831.0	104.7	3422.3	2054.2	1687.2	3519.2	2204.7	1633.6	150.5	-53.6	61.0		1762.4	102.9	1753.9	110.1	2011.5	108.6	3765.4	109.3	3868.0	8.0	4360.0	116.2
2003-12-31	2003	109.9	110.2	109.2	122.3	112.0	135.9	13208.0	107.3	3964.9	2358.6	1984.3	4138.7	2586.2	1930.5	227.6	-53.8	76.1		2186.4	112.7	2091.7	107.7	2438.0	109.7	4529.7	108.8	4171.0	8.2	5499.0	110.9
2004-12-31	2004	108.7	113.0	107.4	117.7	111.7	183.2	17027.0	107.2	4669.7	2698.9	2373.0	5429.9	3428.9	2403.2	730.0	30.2	97.4		2865.0	116.8	2580.3	111.4	3062.2	115.1	5642.5	113.3	4441.0	7.7	6740.0	110.6
2005-12-31	2005	107.6	109.9	106.4	121.0	110.9	240.0	21610.0	106.4	6820.6	3514.3	2941.2	8579.6	5127.2	2999.9	1612.9	58.7	123.8		3611.1	110.2	3217.6	110.5	3823.9	115.1	7041.5	112.8	4550.0	7.1	8555.0	112.6
2006-12-31	2006	110.1	108.4	106.0	113.9	109.0	297.5	26917.0	108.2	8375.2	4284.8	3657.7	10625.8	6278.9	3797.3	1994.1	139.6	163.2		4730.0	117.8	3947.4	111.0	4764.5	116.8	8711.9	114.1	4675.0	7.0	10634.0	113.3
2007-12-31	2007	107.7	117.1	106.5	113.3	111.9	346.5	33248.0	108.5	11378.6	5986.6	4790.5	13368.3	7781.1	4828.5	1794.6	38.0	223.1		6716.2	123.8	4891.4	112.6	5977.6	119.1	10869.0	116.1	4788.0	6.0	13593.0	117.2
2008-12-31	2008	110.9	117.6	108.0	115.9	113.3	466.3	41277.0	105.2	14157.0	7570.9	6253.1	16169.1	9275.9	6198.8	1705.1	-54.4	288.7		8781.6	109.5	6495.7	111.7	7448.5	115.3	13944.2	113.7	4820.0	6.2	17290.0	111.5
2009-12-31	2009	108.9	105.5	109.7	111.6	108.8	297.2	38807.0	92.2	16048.3	9660.1	6255.7	13599.7	7337.8	5926.6	-2322.3	-329.1	183.9		7976.0	86.5	7097.1	98.1	7502.1	91.8	14599.2	94.9	4344.0	8.2	18638.0	96.5
2010-12-31	2010	108.3	113.7	105.0	108.1	108.8	392.7	46308.0	104.5	17616.7	10117.5	6636.9	16031.9	8305.4	6537.3	-1812.0	-99.6	245.7		9152.1	106.3	8002.2	105.1	8509.8	108.0	16512.0	106.5	4645.0	7.3	20952.0	105.2
2011-12-31	2011	108.4	103.2	106.7	108.7	106.1	515.4	59698.0	104.3	19994.6	10925.6	7679.1	20855.4	11367.7	7644.2	442.0	-34.9	318.6		11035.7	110.8	9104.3	103.4	10000.0	110.8	19104.3	107.1	4799.0	6.5	23369.0	102.8
2012-12-31	2012	112.1	106.7	105.2	107.3	106.6	527.4	66927.0	103.5	23174.7	12895.0	8343.2	23435.1	12855.5	8064.5	-39.4	-278.7	335.8		12586.1	106.8	9961.4	103.6	11433.1	108.6	21394.5	106.3	4934.0	5.5	26629.0	108.4
2013-12-31	2013	114.6	106.1	104.5	108.0	106.5	521.8	71017.0	101.3	25290.9	13342.9	8806.6	24442.7	13019.9	8165.1	-323.0	-641.5	341.3		13450.3	100.8	11143.0	102.6	12542.9	104.9	23685.9	103.9	4958.0	5.5	29792.0	104.8
2014-12-31	2014	113.7	115.7	108.1	110.5	111.4	496.8	79200.0	100.7	27611.7	14831.6	9353.3	26766.1	14496.9	8905.7	-334.7	-447.6	307.9		13902.6	98.5	12380.9	100.0	13975.3	105.1	26356.2	102.7	4955.0	5.2	32495.0	101.2
2015-12-31	2015	110.7	114.5	113.7	110.2	112.9	341.5	83233.0	97.2	29741.5	15620.3	9479.8	26922.0	13659.2	9308.2	-1961.0	-171.6	193.0	99.2	13897.2	89.9	13412.3	91.0	14114.5	89.1	27526.8	90.0	4978.0	5.6	34030.0	91.0
2016-12-31	2016	106.4	104.3	106.5	104.9	105.4	281.7	86044.0	99.8	31323.7	16416.4	9936.4	28181.5	13460.0	9923.8	-2956.4	-12.6	191.7	101.3	14639.8	99.1	13751.8	95.0	14565.5	95.8	28317.3	95.4	5070.0	5.5	36709.0	100.8"""

dfq_text = """	year	qtr	CPI_ALCOHOL_rog	CPI_FOOD_rog	CPI_NONFOOD_rog	CPI_SERVICES_rog	CPI_rog	EXPORT_GOODS_bln_usd	GDP_bln_rub	GDP_yoy	GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub	GOV_EXPENSE_ACCUM_FEDERAL_bln_rub	GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub	GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub	GOV_REVENUE_ACCUM_FEDERAL_bln_rub	GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub	GOV_SURPLUS_ACCUM_FEDERAL_bln_rub	GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub	IMPORT_GOODS_bln_usd	INDPRO_rog	INDPRO_yoy	INVESTMENT_bln_rub	INVESTMENT_rog	INVESTMENT_yoy	RETAIL_SALES_FOOD_bln_rub	RETAIL_SALES_FOOD_rog	RETAIL_SALES_FOOD_yoy	RETAIL_SALES_NONFOOD_bln_rub	RETAIL_SALES_NONFOOD_rog	RETAIL_SALES_NONFOOD_yoy	RETAIL_SALES_bln_rub	RETAIL_SALES_rog	RETAIL_SALES_yoy	TRANSPORT_FREIGHT_bln_tkm	UNEMPL_pct	WAGE_NOMINAL_rub	WAGE_REAL_rog	WAGE_REAL_yoy
1999-03-31	1999	1	118.2	118.4	114.0	109.5	116.0	15.3	901.0	98.1	189.0	108.3	91.5	171.9	89.1	93.6	-19.2	2.1	9.1			96.8		93.8	186.8	85.0	92.7	192.2	90.7	84.3	379.0	88.0	88.1	821.0	14.3	1248.0	80.9	60.7
1999-06-30	1999	2	106.8	106.4	108.6	109.0	107.3	17.1	1102.0	103.1	486.8	272.1	240.0	448.6	226.6	247.3	-45.5	7.3	10.1			131.1		99.2	204.3	101.4	91.6	212.2	100.2	88.5	416.5	100.8	90.0	831.0	13.0	1511.0	111.5	65.1
1999-09-30	1999	3	106.0	104.3	107.2	107.2	105.6	18.9	1373.0	111.4	795.8	434.2	400.6	759.3	387.3	411.0	-46.9	10.4	9.5			185.6		105.0	222.6	103.1	89.2	242.0	107.0	91.3	464.6	105.1	90.3	833.0	12.3	1642.0	102.4	76.4
1999-12-31	1999	4	107.1	102.8	104.9	104.7	103.9	24.3	1447.0	112.0	1258.0	666.9	653.8	1213.6	615.5	660.8	-51.4	7.0	10.8			256.9		117.4	252.4	110.3	98.0	284.9	110.8	107.8	537.3	110.6	103.1	887.0	12.5	1927.0	112.9	104.7
2000-03-31	2000	1	114.3	101.4	105.0	108.0	104.1	23.9	1527.0	111.4	330.2	191.5	154.7	366.5	221.8	160.7	30.3	6.0	10.0			165.8		113.5	242.6	92.6	106.9	275.1	92.1	109.5	517.7	92.4	108.2	886.0	12.1	1899.0	94.4	125.3
2000-06-30	2000	2	103.4	106.1	103.5	106.6	105.3	25.5	1697.0	110.2	760.9	405.4	402.7	887.8	507.7	427.3	102.3	24.6	10.4			236.0		119.6	252.5	101.0	106.5	290.3	101.5	110.9	542.8	101.3	108.7	867.0	10.4	2148.0	109.1	122.0
2000-09-30	2000	3	103.3	102.6	104.3	109.8	104.1	26.6	2038.0	110.5	1204.8	632.2	642.3	1395.9	783.2	682.4	151.0	40.1	11.1			330.2		119.7	276.0	103.9	107.3	322.4	107.4	111.3	598.4	105.8	109.4	868.0	9.9	2336.0	103.4	124.7
2000-12-31	2000	4	102.3	106.1	104.6	105.7	105.4	29.1	2044.0	108.2	1960.1	1029.2	1032.1	2097.7	1132.1	1065.8	102.9	33.8	13.4			433.2		116.1	322.1	111.8	108.8	371.3	109.4	110.0	693.4	110.5	109.4	921.0	9.8	2652.0	108.1	117.8"""

dfm_text = """	year	month	CPI_ALCOHOL_rog	CPI_FOOD_rog	CPI_NONFOOD_rog	CPI_SERVICES_rog	CPI_rog	EXPORT_GOODS_bln_usd	GOV_EXPENSE_ACCUM_CONSOLIDATED_bln_rub	GOV_EXPENSE_ACCUM_FEDERAL_bln_rub	GOV_EXPENSE_ACCUM_SUBFEDERAL_bln_rub	GOV_REVENUE_ACCUM_CONSOLIDATED_bln_rub	GOV_REVENUE_ACCUM_FEDERAL_bln_rub	GOV_REVENUE_ACCUM_SUBFEDERAL_bln_rub	GOV_SURPLUS_ACCUM_FEDERAL_bln_rub	GOV_SURPLUS_ACCUM_SUBFEDERAL_bln_rub	IMPORT_GOODS_bln_usd	INDPRO_rog	INDPRO_yoy	INVESTMENT_bln_rub	INVESTMENT_rog	INVESTMENT_yoy	RETAIL_SALES_FOOD_bln_rub	RETAIL_SALES_FOOD_rog	RETAIL_SALES_FOOD_yoy	RETAIL_SALES_NONFOOD_bln_rub	RETAIL_SALES_NONFOOD_rog	RETAIL_SALES_NONFOOD_yoy	RETAIL_SALES_bln_rub	RETAIL_SALES_rog	RETAIL_SALES_yoy	TRANSPORT_FREIGHT_bln_tkm	UNEMPL_pct	WAGE_NOMINAL_rub	WAGE_REAL_rog	WAGE_REAL_yoy
1999-01-31	1999	1	109.7	110.4	106.2	104.1	108.4	4.5	45.6	27.4	22.7	49.0	27.8	25.7	0.4	3.0	2.7			28.5	42.5	92.2	60.3	82.5	90.3	61.5	81.0	79.0	121.8	81.7	84.0	277.7	14.3	1167.0	72.5	58.6
1999-02-28	1999	2	104.2	104.4	104.0	103.2	104.1	4.9	103.1	61.0	49.2	99.3	54.7	51.7	-6.3	2.5	3.0			31.8	108.4	93.8	60.7	96.5	93.7	62.2	97.4	85.4	122.9	96.9	89.2	252.1	14.6	1199.0	99.1	59.0
1999-03-31	1999	3	103.4	102.7	103.2	101.9	102.8	5.8	189.0	108.3	91.5	171.9	89.1	93.6	-19.2	2.1	3.5			36.5	111.2	95.1	65.8	105.5	94.1	68.5	106.6	89.1	134.3	106.0	91.4	291.4	14.0	1385.0	111.7	62.8
1999-04-30	1999	4	103.4	102.5	104.0	103.1	103.0	6.6	285.5	160.1	138.7	264.0	133.9	143.4	-26.2	4.7	3.3			36.9	97.2	94.7	66.2	98.1	90.6	69.2	97.1	87.5	135.4	97.6	88.9	277.1	13.5	1423.0	100.0	64.0
1999-05-31	1999	5	101.8	102.0	102.7	102.1	102.2	5.1	380.8	213.4	185.0	349.9	173.7	193.8	-39.7	8.8	2.9			41.4	109.2	99.2	68.6	101.6	91.8	70.3	98.9	87.8	138.9	100.2	89.7	282.1	12.9	1472.0	101.2	65.1
1999-06-30	1999	6	101.4	101.8	101.6	103.5	101.9	5.4	486.8	272.1	240.0	448.6	226.6	247.3	-45.5	7.3	4.0			52.8	124.3	102.9	69.5	99.6	92.4	72.7	101.8	90.3	142.2	100.7	91.3	271.9	12.8	1626.0	107.7	66.0
1999-07-31	1999	7	102.1	103.3	101.9	103.1	102.8	6.3	588.6	328.9	288.5	550.7	282.1	297.4	-46.8	8.9	3.2			56.2	102.6	102.1	71.6	99.8	90.1	74.2	100.1	88.4	145.8	100.0	89.2	276.2	12.5	1618.0	96.9	65.0
1999-08-31	1999	8	101.9	100.3	102.4	101.9	101.2	6.2	694.4	381.7	345.5	658.7	334.3	356.7	-47.4	11.2	3.1			61.8	106.2	101.9	74.0	102.9	88.5	83.6	110.0	89.0	157.6	106.5	88.8	281.2	12.1	1608.0	98.1	69.3
1999-09-30	1999	9	102.0	100.7	102.7	102.0	101.5	6.4	795.8	434.2	400.6	759.3	387.3	411.0	-46.9	10.4	3.1			67.6	104.1	111.1	77.0	103.2	89.1	84.2	98.2	95.0	161.2	100.5	92.2	275.2	12.2	1684.0	103.1	93.9
1999-10-31	1999	10	101.9	100.7	102.2	102.0	101.4	7.0	897.8	488.8	454.0	868.1	445.6	467.5	-43.2	13.5	3.4			66.5	95.1	114.8	79.1	101.8	94.8	88.0	102.4	108.4	167.1	102.1	101.9	292.8	12.4	1716.0	100.4	97.8
1999-11-30	1999	11	102.2	100.9	101.5	101.7	101.2	7.6	1016.3	540.5	528.0	1006.4	514.9	543.7	-25.6	15.7	3.5			72.0	104.3	112.1	79.1	99.1	94.3	91.1	101.8	109.0	170.2	100.5	101.9	288.9	12.6	1789.0	103.0	102.5
1999-12-31	1999	12	102.8	101.2	101.1	100.9	101.3	9.7	1258.0	666.9	653.8	1213.6	615.5	660.8	-51.4	7.0	4.0			118.4	161.3	122.6	94.2	117.4	104.7	105.8	114.9	106.4	200.0	116.0	105.6	305.6	12.5	2283.0	124.4	113.6
2000-01-31	2000	1	109.2	101.3	102.2	103.4	102.3	6.8	82.9	52.8	34.4	102.0	64.9	41.4	12.1	7.0	2.9			46.1	37.4	107.9	79.5	82.6	104.8	90.8	84.0	110.3	170.3	83.3	107.6	296.6	12.5	1830.0	80.9	126.1
2000-02-29	2000	2	102.8	100.2	101.3	103.0	101.0	8.0	184.8	111.2	82.3	217.4	138.3	87.8	27.1	5.5	3.4			55.8	116.6	116.1	79.2	99.2	107.7	88.9	96.7	109.5	168.1	97.9	108.7	286.1	12.4	1839.0	99.4	126.4
2000-03-31	2000	3	101.8	99.9	101.4	101.5	100.6	9.1	330.2	191.5	154.7	366.5	221.8	160.7	30.3	6.0	3.7			63.9	110.8	115.7	83.9	105.9	108.1	95.4	105.8	108.7	179.3	105.9	108.4	303.4	11.4	2018.0	108.9	123.5
2000-04-30	2000	4	100.8	100.2	101.5	102.1	100.9	8.3	470.0	261.2	230.1	535.0	314.0	242.3	52.8	12.2	3.4			64.5	97.9	116.5	82.3	97.8	107.8	95.5	98.5	110.3	177.8	98.2	109.1	287.5	10.8	2039.0	100.2	123.3
2000-05-31	2000	5	101.2	102.3	101.1	101.3	101.8	8.5	609.5	333.9	311.6	717.7	415.5	338.2	81.6	26.6	3.4			75.8	114.4	122.1	83.7	99.5	105.6	96.1	99.6	111.1	179.8	99.6	108.4	293.4	10.3	2101.0	101.1	122.3
2000-06-30	2000	6	101.4	103.5	100.8	103.0	102.6	8.7	760.9	405.4	402.7	887.8	507.7	427.3	102.3	24.6	3.6			95.7	122.1	120.0	86.5	100.1	106.1	98.7	101.9	111.2	185.2	101.1	108.7	286.2	10.1	2294.0	106.4	121.4
2000-07-31	2000	7	101.5	101.8	100.8	103.8	101.8	8.6	895.4	473.3	478.0	1045.9	596.1	505.7	122.8	27.7	3.6			99.1	100.0	116.9	88.8	100.8	107.2	101.4	101.9	113.1	190.2	101.4	110.2	292.0	10.0	2302.0	98.8	123.1
2000-08-31	2000	8	101.1	100.2	101.4	103.0	101.0	9.1	1058.3	556.0	565.1	1232.3	693.0	602.1	137.0	37.0	3.8			112.9	111.2	122.5	92.5	103.9	108.2	110.1	107.2	110.2	202.6	105.6	109.3	290.0	9.9	2289.0	98.5	123.3
2000-09-30	2000	9	100.7	100.6	102.1	102.8	101.3	9.0	1204.8	632.2	642.3	1395.9	783.2	682.4	151.0	40.1	3.8			118.3	101.7	119.6	94.7	101.7	106.7	110.9	98.7	110.8	205.6	100.1	108.8	285.8	9.8	2367.0	102.1	122.0
2000-10-31	2000	10	100.5	102.4	101.9	102.4	102.1	8.9	1353.1	710.2	720.9	1567.5	880.4	765.1	170.2	44.2	4.1			114.6	94.0	118.2	99.3	102.7	107.6	115.0	101.7	110.1	214.3	102.2	109.0	307.8	9.8	2425.0	100.5	121.9
2000-11-30	2000	11	100.8	101.6	101.5	101.6	101.5	10.1	1536.3	800.0	823.0	1785.0	990.7	881.0	190.7	58.0	4.4			123.0	104.6	118.5	101.5	100.7	109.3	119.0	102.0	110.3	220.5	101.4	109.9	302.1	9.8	2508.0	101.9	119.4
2000-12-31	2000	12	101.1	102.0	101.2	101.6	101.6	10.1	1960.1	1029.2	1032.1	2097.7	1132.1	1065.8	102.9	33.8	4.9			195.5	154.3	113.4	121.3	117.4	109.3	137.3	114.0	109.5	258.6	115.6	109.4	311.0	9.9	3025.0	118.8	113.4"""

dfa = to_dataframe(dfa_text)
# assert dfa.index[0] == pd.Timestamp("1999-12-31")
dfq = to_dataframe(dfq_text)
dfm = to_dataframe(dfm_text)


# TODO <https://github.com/epogrebnyak/mini-kep/issues/61>

# Check on resulting dataframes dfa, dfq, dfm based on following rules:
#  1. absolute values by month/qtr accumulate to qtr/year (with some delta for rounding)
#  2. rog rates accumulate to yoy (with some delta for rounding)
#  3. formulate other checks


# checking 1

def sum_to_quarter(ts):
    ts = ts.resample('QS').sum()
    ts.index += pd.offsets.QuarterEnd()
    return ts


def sum_to_year(ts):
    return ts.resample('A').sum()


def rog_to_yoy(ts):
    return (ts / 100).resample('A').prod()


def error(ts, ref_ts, grouper_func):
    return abs(grouper_func(ts) - ref_ts).dropna()


# demo rounding error proportions
true_values = [0.049, 0.049, 0.049]
rounded_values = [round(x, 1) for x in true_values]
rounding_error = sum(true_values) - sum(rounded_values)
assert rounding_error > 0.05 * 3 - 0.03


# ----- exprimental class
# FIXME: possibly refactor as LevelErrors and GrowthRateErrors

class TypeErrorManager:
    DirectionType = [['m2q', 'm2a', 'q2a'], ['r2y']]

    def __init__(self, error_type):
        self.error_type = error_type

<<<<<<< HEAD
    DefaultThreshold = [
        dict(
            m2q=0.05 * 3,
            m2a=0.05 * 12,
            q2a=0.05 * 4),
        dict(
            r2y=0.15)]
=======
    def _get_directions(self):
        return self.DirectionType[self.error_type]
>>>>>>> 9f4277e20d64def1f5640a8b065dc1f8c01820d1

    def _get_error(self, direction):
        if self.error_type == 0:
            df_error = dict(m2q=self.m2q, m2a=self.m2a, q2a=self.q2a)[direction]
        elif self.error_type == 1:
            df_error = self.r2y

        return df_error

    def _calculate_errors(self, varname):
        if self.error_type == 0:
            tsm = dfm[varname]
            tsq = dfq[varname]
            tsa = dfa[varname]

            self.m2q = error(tsm, tsq, sum_to_quarter)
            self.m2a = error(tsm, tsa, sum_to_year)
            self.q2a = error(tsq, tsa, sum_to_year)

        elif self.error_type == 1:
            tsm = dfm[varname + 'rog']
            tsa = dfa[varname + 'yoy'] / 100

            self.r2y = error(tsm, tsa, rog_to_yoy)


class Errors:
    DefaultThreshold = [dict(m2q=0.05 * 3, m2a=0.05 * 12, q2a=0.05 * 4), dict(r2y=0.15)]

    def __init__(self, varname, error_type):
        # FIXME: globals here not good

        self.error_manager = TypeErrorManager(error_type)
        self.error_manager._calculate_errors(varname)

    def _get_failed(self, direction, threshold=False):
        if not threshold:
            threshold = self.DefaultThreshold[self.error_manager.error_type][direction]

<<<<<<< HEAD
        df_error = None
        if self.error_type == 0:
            df_error = dict(
                m2q=self.m2q,
                m2a=self.m2a,
                q2a=self.q2a)[direction]
        elif self.error_type == 1:
            df_error = self.r2y
=======
        df_error = self.error_manager._get_error(direction)
>>>>>>> 9f4277e20d64def1f5640a8b065dc1f8c01820d1

        # form fucntions below
        return df_error.where(df_error > threshold).dropna()

    def _is_valid_on_direction(self, direction):
        return self._get_failed(direction).empty

    def is_valid(self):
        return all(self._is_valid_on_direction(d) for d in self.error_manager._get_directions())


# ----- end exprimental class


def check_levels_aggregate_up(varnames, error_type):
    return [Errors(varname, error_type).is_valid() for varname in varnames]


labels = [lab for lab in dfa.columns if 'rub' in lab or 'usd' in lab]
labels = ['EXPORT_GOODS_bln_usd', 'IMPORT_GOODS_bln_usd']
<<<<<<< HEAD

=======
>>>>>>> 9f4277e20d64def1f5640a8b065dc1f8c01820d1

err = Errors('EXPORT_GOODS_bln_usd', 0)
assert err._get_failed('m2q').empty
assert err._get_failed('m2a').empty
assert err._get_failed('q2a').empty

err1 = Errors('RETAIL_SALES_', 1)
assert err1._get_failed('r2y').empty

# TODO: add testing with different thrseholds


if __name__ == '__main__':
    varnames = ['EXPORT_GOODS_bln_usd', 'IMPORT_GOODS_bln_usd']
    is_passed = all(check_levels_aggregate_up(varnames, 0))
    print('Month/quarter aggregation test passed:', is_passed)

    # TODO: must pick all testable variables, present in dfa, dfq, dfm
    labels = [lab for lab in dfa.columns if 'rub' in lab or 'usd' in lab]
<<<<<<< HEAD
    #is_passed = all(check_levels_aggregate_up(labels))
    #print('Month/quarter aggregation test passed:', is_passed)
    labels2 = set([lab[0: len(lab) - 3]
                   for lab in dfm.columns if 'rog' in lab or 'yoy' in lab])
=======
    # is_passed = all(check_levels_aggregate_up(labels))
    # print('Month/quarter aggregation test passed:', is_passed)
    labels2 = set([lab[0: len(lab) - 3] for lab in dfm.columns if 'rog' in lab or 'yoy' in lab])
>>>>>>> 9f4277e20d64def1f5640a8b065dc1f8c01820d1
    labels3 = []
    for label in labels2:
        if (label + 'rog') in dfm.columns and (label + 'yoy') in dfa.columns:
            labels3.append(label)

    varnames = [
        'INVESTMENT_',
        'RETAIL_SALES_FOOD_',
        'RETAIL_SALES_',
        'RETAIL_SALES_NONFOOD_',
        'INDPRO_',
        'WAGE_REAL_']

    is_passed = check_levels_aggregate_up(varnames, 1)
    print('Rog -> yoy check ', is_passed)

<<<<<<< HEAD
    # TODO: write test for GDP and INVESTMENT
=======



    # TODO: write test for GDP and INVESTMENT


>>>>>>> 9f4277e20d64def1f5640a8b065dc1f8c01820d1


# BAD_RESULT = pd.DataFrame({'A': [1]})

#
# def check_month_to_year(month_frame, quarter_frame, year_frame, acceptable_error,
#                        variable_to_check='EXPORT_GOODS_bln_usd'):
#    """
#        Check consistency sum of particular column in month_frame and year_frame
#
#        Args:
#             month: month data frame
#             quarter_frame: quarter data frame.
#             year_frame: year data frame
#             acceptable_error: acceptable_error of consistency
#             variable_to_check: column_name which we will check
#
#        Returns:
#            True, if we have not found unconsistent entry else: False
#     """
#
#    try:
#        monthly = month_frame[variable_to_check]
#        annual = year_frame[variable_to_check]
#
#        month_to_year = monthly.resample('A').sum()
#        month_to_year.index += pd.offsets.YearEnd()
#
#        error_month_to_year = (month_to_year - annual).abs()
#
#        error_month_to_year.dropna(inplace=True)
#
#        return error_month_to_year.where(error_month_to_year >= acceptable_error).dropna().empty
#
#    #        assert (error_month_to_year < acceptable_error).all()
#
#    except KeyError:
#        pass
#
#    return False
#
#
# def check_month_to_qtr(month_frame, quarter_frame, year_frame, acceptable_error,
#                       variable_to_check='EXPORT_GOODS_bln_usd'):
#    """
#        Check consistency sum of particular column in month_frame and year_frame
#
#        Args:
#             month: month data frame
#             quarter_frame: quarter data frame.
#             year_frame: year data frame
#             acceptable_error: acceptable_error of consistency
#             variable_to_check: column_name which we will check
#
#        Returns:
#            True, if we have not found unconsistent entry else: False
#     """
#
#    try:
#        monthly = month_frame[variable_to_check]
#        qtr = quarter_frame[variable_to_check]
#
#        month_to_qtr = monthly.resample('QS').sum()
#        month_to_qtr.index += pd.offsets.QuarterEnd()
#        error_month_to_qtr = (month_to_qtr - qtr).abs()
#        error_month_to_qtr.dropna(inplace=True)
#
#        return error_month_to_qtr.where(error_month_to_qtr >= acceptable_error).dropna().empty
#
#    #        assert (error_month_to_qtr < acceptable_error).all()
#
#    except KeyError:
#        pass
#
#    return False
#
#
# def check_qtr_to_year(month_frame, quarter_frame, year_frame, acceptable_error,
#                      variable_to_check='EXPORT_GOODS_bln_usd'):
#    """
#        Check consistency sum of particular column in month_frame and year_frame
#
#        Args:
#             month: month data frame
#             quarter_frame: quarter data frame.
#             year_frame: year data frame
#             acceptable_error: acceptable_error of consistency
#             variable_to_check: column_name which we will check
#
#        Returns:
#            True, if we have not found unconsistent entry else: False
#    """
#
#    try:
#        qtr = quarter_frame[variable_to_check]
#        annual = year_frame[variable_to_check]
#
#        qtr_to_year = qtr.resample('A').sum()
#        qtr_to_year.index += pd.offsets.YearEnd()
#        error_qtr_to_year = (qtr_to_year - annual).abs()
#        error_qtr_to_year.dropna(inplace=True)
#
#        return error_qtr_to_year.where(error_qtr_to_year >= acceptable_error).dropna().empty
#
#    except KeyError:
#        pass
#
#    return False
#
#
# if __name__ == "__main__":
#
#
#    columns_passed = [column for column in dfm.columns
#                      if check_month_to_year(dfm, dfq, dfa, 0.15, column)]
#
#    print("Column passed for month->year ", columns_passed)
#
#    columns_passed = [column for column in dfm.columns
#                      if check_month_to_qtr(dfm, dfq, dfa, 0.1, column)]
#
#    print("Column passed for month->qtr ", columns_passed)
#
#    columns_passed = [column for column in dfm.columns
#                      if check_qtr_to_year(dfm, dfq, dfa, 0.15, column)]
#
#    print("Column passed for qtr->year ", columns_passed)
