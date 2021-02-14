# Ikaros
Ikaros is a free financial library built in pure python that can be used to get information for single stocks, generate signals and build prortfolios 


# How to use

## Stock

The Stock object is a representation of all information what is available for a given security. For example for *AAPL* we scrape information from -

https://finviz.com/quote.ashx?t=AAPL
https://www.zacks.com/stock/research/AAPL/earnings-announcements

We also use the Yahoo Finance Library: yahooquery (GitHub link - https://github.com/dpguthrie/yahooquery ) to  get fundamental data and price data.

```python
>>>> from Stock import Stock
>>>> aapl = Stock('AAPL')
>>>> aapl.financial_data
             AccountsPayable  ...  WorkingCapital
ReleaseDate                   ...                
2020-01-28      4.511100e+10  ...    6.107000e+10
2020-04-30      3.242100e+10  ...    4.765900e+10
2020-07-30      3.532500e+10  ...    4.474700e+10
2020-10-29      4.229600e+10  ...    3.832100e+10
2021-01-27      6.384600e+10  ...    2.159900e+10

[5 rows x 129 columns]

>>>> aapl['PriceClose']
date
2018-02-15     41.725037
2018-02-16     41.589962
2018-02-20     41.450069
2018-02-21     41.261936
2018-02-22     41.606850
   
2021-02-08    136.910004
2021-02-09    136.009995
2021-02-10    135.389999
2021-02-11    135.130005
2021-02-12    135.369995
Name: PriceClose, Length: 754, dtype: float6
```

Mix and match market data with fundamental data directly. Ikaros uses the earnings calendar from Zacks to get an accurate Point in time, timeseries from fundamental data.

```python
>>>> aapl['PriceClose'] / aapl['TotalRevenue']
date
2018-02-15             NaN
2018-02-16             NaN
2018-02-20             NaN
2018-02-21             NaN
2018-02-22             NaN
    
2021-02-08    1.228565e-09
2021-02-09    1.220488e-09
2021-02-10    1.214925e-09
2021-02-11    1.212592e-09
2021-02-12    1.214745e-09
Length: 754, dtype: float64
```

