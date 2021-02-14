# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 13:55:33 2021

@author: saidsa
"""

import numpy as np
import pandas as pd


def Price_to_Sales_Signal (stock_object, raw = True, window = 21):
    if raw:
        return stock_object['PriceClose'] / stock_object['TotalRevenue']
    else:
        return (stock_object['PriceClose'] / stock_object['TotalRevenue']).rolling(window = window).apply(lambda x: (x[-1] - x[0:-1].mean())/(x[0:-1].std()))
      
        
def Quick_Ratio_Signal(stock_object,  raw = True, window = 21):
    raw_signal = (stock_object['CurrentAssets'] - stock_object['Inventory'])\
            / stock_object['CurrentLiabilities']
    if raw:
        return raw_signal
    else:
        return raw_signal.rolling(window = window).apply(lambda x: (x[-1] - x[0:-1].mean())/(x[0:-1].std()))
        
    
def Insider_Flow_Signal(stock_obj, window=90, hl = 45):
    insider_trade_df = stock_obj.insider_trading_data
    insider_trade_df['Sign'] = insider_trade_df['Transaction'].apply( lambda x: -1 if x == 'Sale' else 1 if x == 'Buy' else 0 )
    insider_trade_df['NetValue'] = insider_trade_df['Value'] * insider_trade_df['Sign']
    insider_trade_df['Datetime'] = pd.to_datetime(insider_trade_df['Date'])
    
    raw_weights= np.array([(0.5**(1/hl))**i  for i in range(window-1,-1,-1)])
    scaled_weights =  window * (raw_weights / sum(raw_weights))
    net_value_ts = insider_trade_df.set_index('Datetime')\
                                .loc[:, 'NetValue'].resample('D')\
                                .sum().rolling(window=window)\
                                .apply(lambda x: sum(x * scaled_weights))
                                
    net_value_ts.index = net_value_ts.index.map(lambda x: x.date())
    mkt_value_ts = stock_obj['ShareIssued']*stock_obj['PriceClose']
    signal_ts = net_value_ts/mkt_value_ts
    signal_ts = signal_ts.loc[stock_obj['PriceClose'].index] 
    return signal_ts


def Price_target_to_Price_Signal(stock_obj):
    ratings_df = stock_obj.ratings_data
    ratings_df['DateTime'] =  pd.to_datetime(ratings_df['RatingDate'])
    PT_ts = ratings_df.set_index('DateTime').loc[:, 'NewPT'].resample('D').mean()
    PT_ts.index = PT_ts.index.map(lambda x: x.date())
    PT_ts = PT_ts.reindex(stock_obj['PriceClose'].index).ffill()
    signal_ts = (PT_ts - stock_obj['PriceClose']) / stock_obj['PriceClose']
    return signal_ts
    

