# Ikaros
Ikaros is a free financial library built in pure python that can be used to get information for single stocks, generate signals and build prortfolios 


# How to use

## Stock

The Stock object is a representation of all information what is available for a given security. For example for *AAPL* we scrape information from -

1. https://finviz.com/quote.ashx?t=AAPL
2. https://www.zacks.com/stock/research/AAPL/earnings-announcements

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
Ikaros also caches the data webscraped into readable csv files. If you want to save the data in a custom location, ensure that the enviornment variable *IKAROSDATA* is set on your operating system.

## Signal

The Signal Library is repository of functions that provide useful insights into stocks. We have a limited number of signals so far but stay tuned! for more

```python

>>>> from Signals import Quick_Ratio_Signal
>>>> ford = Stock('F')
>>>> Quick_Ratio_Signal(ford)
date
2018-02-15         NaN
2018-02-16         NaN
2018-02-20         NaN
2018-02-21         NaN
2018-02-22         NaN
  
2021-02-08    1.089966
2021-02-09    1.089966
2021-02-10    1.089966
2021-02-11    1.089966
2021-02-12    1.089966
Length: 754, dtype: float64

>>>> Quick_Ratio_Signal(ford, raw=False, window=21) # Computes the rolling 21 day Z-score
date
2018-02-15         NaN
2018-02-16         NaN
2018-02-20         NaN
2018-02-21         NaN
2018-02-22         NaN
  
2021-02-08    4.248529
2021-02-09    2.924038
2021-02-10    2.320201
2021-02-11    1.949359
2021-02-12    1.688194
Length: 754, dtype: float64

```

## Portfolio

Finally, use the signals and stock objects to construct Portfolios yourself. Currently we have 
1. Pair Trading Portfolio for 2 Stocks and a Signal
2. Singal Signal Portfolio for multiple Sotcks given a Signal
3. A basic implementation of the Black Litterman Model

For a **PairTradingPortfolio**, lets look at *GM* and *Ford* and compare the two based on the *Quick Ratio*

```python
>>>> from Stock import Stock
>>>> from Signals import Quick_Ratio_Signal
>>>> from Portfolio import PairTradingPortfolio
>>>> ford = Stock('F')
>>>> gm = Stock('GM')
>>>> ptp = PairTradingPortfolio(stock_obj1=ford, stock_obj2=gm, signal_func=Quick_Ratio_Signal)
>>>> ptp.relative_differencing() # The weights are set based on the rolling z-score of the difference of the signals for the 2 stocks
>>>> ptp.get_returns()
date
2018-02-15         NaN
2018-02-16         NaN
2018-02-20         NaN
2018-02-21         NaN
2018-02-22         NaN
  
2021-02-08   -0.033217
2021-02-09    0.037791
2021-02-10    0.005568
2021-02-11   -0.001001
2021-02-12   -0.001700
Length: 754, dtype: float64
>>>> ptp.stock_obj1_wght_ts # Get the weight of Stock 1 ( Weight of stock 2 is just -1 times weight of stock 1)
Out[9]: 
date
2018-02-15         NaN
2018-02-16         NaN
2018-02-20         NaN
2018-02-21         NaN
2018-02-22         NaN
  
2021-02-08    0.814045
2021-02-09    0.818967
2021-02-10    0.823901
2021-02-11    0.909396
2021-02-12    0.910393
Length: 754, dtype: float64
```
