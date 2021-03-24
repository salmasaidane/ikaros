# Ikaros
Ikaros is a free financial library built in pure python that can be used to get information for single stocks, generate signals and build portfolios 


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

>>>> from SignalTransformers import Z_Score
>>>> Z_Score(Quick_Ratio_Signal(ford), window = 21) # Computes the rolling 21 day Z-score
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
2. Single Signal Portfolio for multiple Sotcks given a Signal
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


For a **SingleSignalPortfolio**, lets look at *FaceBook*, *Microsfot* and *Apple* and compare them based on the *Price to Sales Ratio*.

```python
>>>> from Stock import Stock
>>>> from Signals import Price_to_Sales_Signal
>>>> from Portfolio import SingleSignalPortfolio
>>>> from SignalTransformers import Z_Score
>>>> fb = Stock('FB')
>>>> msft = Stock('MSFT')
>>>> aapl = Stock('AAPL')
>>>> signal_func = lambda stock_obj : Z_Score(Price_to_Sales_Signal(stock_obj), window=42) # Use a rolling Z score over 42 days rather than the raw ratio
>>>> ssp = SingleSignalPortfolio([fb, msft, aapl], signal_func)
>>>> ssp.relative_ranking() # Rank the stock from -1 to +1, in this case we have 3 stocks it will be {-1, 0, 1}, if we have 4 sotck it would be {-1, -0.33, 0.33, 1}
>>>> ssp.weight_df
             FB  MSFT  AAPL
date                       
2018-02-15  0.0   0.0   0.0
2018-02-16  0.0   0.0   0.0
2018-02-20  0.0   0.0   0.0
2018-02-21  0.0   0.0   0.0
2018-02-22  0.0   0.0   0.0
        ...   ...   ...
2021-02-08  0.0   1.0  -1.0
2021-02-09  0.0   1.0  -1.0
2021-02-10  0.0   1.0  -1.0
2021-02-11  0.0   1.0  -1.0
2021-02-12  0.0   1.0  -1.0

[754 rows x 3 columns]
>>>> ssp.get_returns() # Initial values are 0 since signal is not available at the start for any of the stocks
date
2018-02-15    0.000000
2018-02-16    0.000000
2018-02-20    0.000000
2018-02-21    0.000000
2018-02-22    0.000000
  
2021-02-08    0.000018
2021-02-09    0.011935
2021-02-10    0.000661
2021-02-11    0.008798
2021-02-12    0.000269
Length: 754, dtype: float64
```

For a **SimpleBlackLitterman**, we can provide multiple stocks and multiple signals. Let us try to look at *Ford*, *GM* and *Toyota* based on the *Price to Sales* and *Quick Ratio*

```python
>>>> from datetime import datetime
>>>> from Stock import Stock
>>>> from Signals import Quick_Ratio_Signal, Price_to_Sales_Signal
>>>> from Portfolio import SimpleBlackLitterman
>>>> from SignalTransformers import Z_Score
>>>> ford = Stock('F')
>>>> gm = Stock('GM')
>>>> toyota = Stock('TM')
>>>> signal_func1 = lambda stock_obj: Quick_Ratio_Signal(stock_obj) # Use the Raw quick Ratio
>>>> signal_func2 = lambda stock_obj: Z_Score(-1*Price_to_Sales_Signal(stock_obj), window=63) # Use the moving 63 Z score for Price to Sales. -1 to Flip the signal
>>>> signal_view_ret_arr = [0.02, 0.01] # Expected returns from each signal. Typically denoted as Q
>>>> sbl = SimpleBlackLitterman(stock_arr=[ford, gm, toyota], signal_func_arr=[signal_func1, signal_func2], signal_view_ret_arr=signal_view_ret_arr)
>>>> dt = datetime(2021, 2, 12).date()
>>>> sbl.weights_df # Weights based on MarketCap
                   F        GM        TM
date                                    
2020-02-07  0.059205  0.085642  0.855153
2020-02-10  0.059145  0.087673  0.853182
2020-02-11  0.059010  0.088974  0.852016
2020-02-12  0.059782  0.089820  0.850399
2020-02-13  0.060360  0.090068  0.849572
             ...       ...       ...
2021-02-08  0.075640  0.127209  0.797151
2021-02-09  0.077582  0.124607  0.797810
2021-02-10  0.073859  0.117810  0.808331
2021-02-11  0.073232  0.116954  0.809814
2021-02-12  0.072642  0.116230  0.811128

[257 rows x 3 columns]
>>>> sbl.var_covar_ts[dt] # Variance Covariance Martix computed based on rolling 126 days of returns, var_covar_ts is a dict of dataframes. Typically denoted as Sigma
           F        GM        TM
F   0.140825  0.085604  0.021408
GM  0.085604  0.197158  0.020909
TM  0.021408  0.020909  0.044832
>>>> sbl.implied_returns_df # Implied Returns for each day. This is often denoted as Pi
                   F        GM        TM
2020-02-10  0.012125  0.016345  0.014762
2020-02-11  0.012131  0.016199  0.014818
2020-02-12  0.011994  0.016279  0.014773
2020-02-13  0.012199  0.016374  0.014645
2020-02-14  0.011042  0.014466  0.013649
             ...       ...       ...
2021-02-08  0.038776  0.047958  0.037335
2021-02-09  0.039060  0.049541  0.037451
2021-02-10  0.038827  0.048351  0.037453
2021-02-11  0.036424  0.045034  0.040050
2021-02-12  0.037661  0.046260  0.040319

[256 rows x 3 columns]
>>>> sbl.link_mat_ts[dt] # The link matrix on a given day. link_mat_ts is a dict of dataframes. Typically denoted as Sigma
            F   GM   TM
signal_0  1.0 -1.0  0.0
signal_1 -1.0  0.0  1.0
>>>> sbl.view_var_covar_ts[dt] # The View variance covariance matrix on a given day. view_var_covar_ts is a dict of dataframes. Typically denoted as Omega
          signal_0  signal_1
signal_0  0.166775 -0.043777
signal_1 -0.043777  0.142840
>>>> sbl.black_litterman_weights_df # The Black litterman weights over time, based on the changing views
                   F        GM        TM
2020-05-07  0.077305  0.127350  0.795345
2020-05-08  0.077354  0.130177  0.792469
2020-05-11  0.077862  0.132684  0.789454
2020-05-12  0.065264  0.071459  0.863277
2020-05-13  0.114959  0.074012  0.811028
             ...       ...       ...
2021-02-08  0.116730  0.123745  0.759526
2021-02-09  0.116043  0.127209  0.756747
2021-02-10  0.149960  0.232889  0.617152
2021-02-11  0.109802 -0.032208  0.922406
2021-02-12  0.107529 -0.033443  0.925915
```
### Update 13/03/2021:

We have added Fama French Factors and some regression utilities for users to be able to look at Fama French factor exposure and incorporate it into their portfolio construction process. Small example below:

```python
>>>> from Stock import Stock
>>>> from Signals import Fama_French_Rolling_Beta
>>>> from Portfolio import SingleSignalPortfolio
>>>> fb = Stock('FB')
>>>> msft = Stock('MSFT')
>>>> aapl = Stock('AAPL')
```
We start off by creating some stock objects and calling a few imports. Next we need to fix our signal function. To do this we use the *Fama_French_Rolling_Beta* import by fixing the Fama_French series name and the regression window.
```python
>>>> Fama_French_HML_42d_Rolling_Beta = lambda x: Fama_French_Rolling_Beta(stock_obj = x, Fama_French_Series_Name = 'HML', window = 42)
>>>> ssp = SingleSignalPortfolio([fb, msft, aapl], Fama_French_HML_42d_Rolling_Beta)
>>>> ssp.relative_ranking()
>>>> ssp.get_returns()
```
### Update 20/03/2021:

We can use the Fama French factors as hedging factors in our portfolios. As an example, we will run a Mean_Variance Optimization problem where we try to maximize expected returns based on momentum and set the portfolio risk level while ensuring that the portfolio long short is $ neutral and hedged against the Fama French market factor.

```python
>>>> from Stock import Stock
>>>> from Signals import Fama_French_Rolling_Beta
>>>> from Signals import Momentum_window
>>>> from Portfolio import SingleSignalHedgedPortfolio
>>>> fb = Stock('FB')
>>>> msft = Stock('MSFT')
>>>> aapl = Stock('AAPL')
>>>> gm = Stock('GM')
>>>> ford = Stock('F')
>>>> toyota = Stock('TM')
>>>> momentum_1_month = lambda x: Momentum_window(stock_obj = x, window = 21)
>>>> ff_mkt_126_day = lambda x: Fama_French_Rolling_Beta(stock_obj = x, Fama_French_Series_Name='Mkt-RF', window = 126)
>>>> sshp = SingleSignalHedgedPortfolio(stock_obj_arr = [aapl, fb, gm, toyota, msft, ford], signal_func = momentum_1_month, hedge_signal_func = ff_mkt_126_day)
>>>> sshp.weights
 
                AAPL        FB        GM        TM      MSFT         F
2018-09-19 -1.015144 -0.800390 -0.864789  1.001281  1.005075  0.673968
2018-09-20 -0.438238 -0.797528 -0.748085  1.250913  0.895315 -0.162375
2018-09-21  0.473650 -1.068282 -0.657205  0.325068  0.721083  0.205687
2018-09-24 -0.126392 -1.042924 -0.691608 -0.769358  0.741956  1.888326
2018-09-25  0.424757 -1.101550 -0.524593 -0.038464  1.180868  0.058982
             ...       ...       ...       ...       ...       ...
2021-02-22 -0.513552 -0.757754 -0.746238 -0.234548  1.547468  0.704624
2021-02-23 -1.042702 -0.298998 -0.543532 -0.399754  1.676662  0.608324
2021-02-24 -1.088975 -0.299291 -0.467647 -0.297045  1.829545  0.323412
2021-02-25 -0.880020 -0.403605 -0.648693 -0.465087  1.367805  1.029600
2021-02-26 -0.876299 -0.385701 -0.635519 -0.491271  1.340112  1.048678

[614 rows x 6 columns]
```
