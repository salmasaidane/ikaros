# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 13:59:04 2021

@author: youss
"""

import pandas as pd
import numpy as np
from Stock import Stock
from scipy.stats import norm

def normalize (x):
    x[x>0.001] = x[x>0.001] / x[x>0.001].sum()
    x[x<0.001] = x[x<0.001] / - x[x<0.001].sum()
    return x



class BlackLitterman(object):

    def build_view(signal_func, stock_arr, n_buckets = None):
        stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
        output_dict = {}
        for s in stock_arr:
            output_dict[s.ticker] = signal_func(s)
        signal_df = pd.DataFrame(output_dict).dropna()
        if n_buckets is None:
            view_df = signal_df.rank(pct = True, axis = 1).apply(lambda x: x - x.mean(), axis = 1).apply(lambda x: normalize(x), axis = 1)
        else:
            view_df = signal_df.apply(lambda x: pd.qcut(x, n_buckets, labels = False), axis = 1)
            big_bucket_idx = view_df == (n_buckets - 1)
            small_bucket_idx = view_df == 0
            view_df.loc[:,:] = 0
            view_df[big_bucket_idx] = 1
            view_df[small_bucket_idx] = -1
            view_df = view_df.apply(lambda x: normalize(x), axis = 1)
    
        return view_df
      
    '''      
    signal_func = lambda s: (s['PriceClose'] / s['TotalRevenue']).rolling(window=21).apply(lambda x: (x[-1] - x.mean())/(x.std()))
      
    df = build_view(signal_func, stock_arr = ['FB', 'AAPL', 'MSFT', 'NFLX', 'GOOGL'], n_buckets = 3)
    '''      
            
    def build_returns (stock_arr):
        stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
        output_dict = {}
        for s in stock_arr:
            output_dict[s.ticker] = s['PriceClose']
        price_df = pd.DataFrame(output_dict).dropna()
        returns_df = price_df.pct_change(1)
        return returns_df
    
    def build_weights (stock_arr):
        stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
        output_dict = {}
        for s in stock_arr:
            output_dict[s.ticker] = s['PriceClose'] * s['ShareIssued']
        marketcap_df = pd.DataFrame(output_dict).dropna()   
        weights_df = marketcap_df.apply(lambda x: normalize(x), axis = 1)
        return weights_df
    
    def black_litterman_weights(stock_universe, view_arr, tau=1.0, lam=0.5 ):
        stock_universe = [Stock(s) if isinstance(s, str) else s for s in stock_universe]   
        weights_df = build_weights(stock_universe).iloc[-1,:]
        returns_df = build_returns(stock_universe)
        Sigma = returns_df.cov() * 252  
        Pi = 2 * lam * Sigma.dot(weights_df)
        


class PairTradingPortfolio(object):
    
    def __init__(self, stock_obj1 , stock_obj2, signal_func, flip_signal=False):
        self.stock_obj1 = stock_obj1
        self.stock_obj2 = stock_obj2
        self.signal_func = signal_func
        self.flip_signal = flip_signal
        self.stock_obj1_signal_ts = signal_func(stock_obj1)
        self.stock_obj2_signal_ts = signal_func(stock_obj2)
        self.relative_signal_ts = None
        self.stock_obj1_wght_ts = None
        self.stock_obj2_wght_ts = None
        self.stock_obj1_return = self.stock_obj1['PriceClose'].pct_change(1)
        self.stock_obj2_return = self.stock_obj2['PriceClose'].pct_change(1)        
        
        
    def relative_scaling(self, window = 90):
        self.relative_signal_ts = (self.stock_obj1_signal_ts / self.stock_obj2_signal_ts).rolling(window = window).apply(lambda x: (x[-1] - x[0:-1].mean())/(x[0:-1].std()))
        if self.flip_signal:
            self.relative_signal_ts = -1 * self.relative_signal_ts
        self.stock_obj1_wght_ts = self.relative_signal_ts.apply(lambda x: (norm.cdf(x) * 2) - 1)
        self.stock_obj2_wght_ts = -1 * self.stock_obj1_wght_ts

        self.portfolio_return_ts = self.stock_obj1_wght_ts.shift(1) * self.stock_obj1_return + \
        self.stock_obj2_wght_ts.shift(1) * self.stock_obj2_return
    
    def relative_differencing(self, window = 90):
        self.relative_signal_ts = (self.stock_obj1_signal_ts - self.stock_obj2_signal_ts).rolling(window = window).apply(lambda x: (x[-1] - x[0:-1].mean())/(x[0:-1].std()))
        if self.flip_signal:
            self.relative_signal_ts = -1 * self.relative_signal_ts
        self.stock_obj1_wght_ts = self.relative_signal_ts.apply(lambda x: (norm.cdf(x) * 2) - 1)
        self.stock_obj2_wght_ts = -1 * self.stock_obj1_wght_ts

        self.portfolio_return_ts = self.stock_obj1_wght_ts.shift(1) * self.stock_obj1_return + \
        self.stock_obj2_wght_ts.shift(1) * self.stock_obj2_return
    
    def get_returns(self):
        self.portfolio_return_ts = self.stock_obj1_wght_ts.shift(1) * self.stock_obj1_return + \
        self.stock_obj2_wght_ts.shift(1) * self.stock_obj2_return
        return self.portfolio_return_ts
    
        
        
class SingleSignalPortfolio(object):

    def __init__(self, stock_obj_arr, signal_func):
        self.stock_obj_arr = stock_obj_arr
        self.signal_func = signal_func
        self.n_stocks = len(stock_obj_arr)
        self.signal_df = None
        returns_dict = {}
        for stock_obj in self.stock_obj_arr:
            returns_dict[stock_obj.ticker] = stock_obj['PriceClose'].pct_change(1)
        self.returns_df = pd.DataFrame(returns_dict).dropna()
        
        
    def relative_ranking(self):
        signal_dict = {}
        for stock_obj in self.stock_obj_arr:
            stock_signal_ts = self.signal_func(stock_obj)
            stock_ticker = stock_obj.ticker
            signal_dict[stock_ticker] = stock_signal_ts
        self.signal_df = pd.DataFrame(signal_dict)
        self.weight_df = self.signal_df.apply( lambda x: 2*((x.rank() - 1) / ( np.sum(~np.isnan(x)) - 1)) - 1, axis=1).fillna(0)
        pass
    
    def get_returns(self):
        self.portfolio_return_ts = (self.weight_df.shift(1) * self.returns_df).sum(axis = 1)
        return self.portfolio_return_ts
        
        
        
        
        
        
        
        
        
        
        






