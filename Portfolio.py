# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 13:59:04 2021

@author: youss
"""
from copy import deepcopy
import pandas as pd
import numpy as np
from numpy.linalg import inv
from Stock import Stock
from scipy.stats import norm

def normalize (x):
    x[x>0.001] = x[x>0.001] / x[x>0.001].sum()
    x[x<0.001] = x[x<0.001] / - x[x<0.001].sum()
    return x


class SimpleBlackLitterman(object):

    def __init__(self, stock_arr, signal_func_arr, signal_view_ret_arr,
                 A=1.0, tau=1.0, shrinkage_factor=0.80):
        
        
        self.stock_arr = [Stock(s) if isinstance(s, str) else s for s in stock_arr]
        
        self.signal_func_arr = signal_func_arr
        self.signal_view_ret_arr = signal_view_ret_arr
        self.A = A
        self.tau = tau
        self.shrinkage_factor = shrinkage_factor
        
        self.returns_df = self.build_returns()
        self.returns_shifted_df = self.returns_df.shift(1)
        
        self.weights_df = self.build_weights()
        self.weights_shifted_df = self.weights_df.shift(1)
        
        self.var_covar_ts = self.generate_varcovar_mats()
        self.inv_var_covar_ts = self.generate_inv_varcovar_mats()
        
        self.implied_returns_df = self.generate_implied_returns()
        self.signal_df_dict = {'signal_'+str(i):self.build_signal_df(sf).dropna() \
                               for i, sf in enumerate(self.signal_func_arr)}
        
        self.signal_ts_dict = self.generate_signal_ts_dict()
        self.link_mat_ts = self.generate_link_mats()
        
        self.view_var_covar_ts = self.generate_view_var_covar_mats()
        self.view_inv_var_covar_ts = self.generate_view_inv_var_covar_mats()

        self.black_litterman_weights_df = self.generate_black_litterman_weights()
        
    def build_returns(self):        
        output_dict = {}
        for s in self.stock_arr:
            output_dict[s.ticker] = s['PriceClose']
        price_df = pd.DataFrame(output_dict)
        returns_df = price_df.pct_change(1)
        return returns_df.dropna()

    def build_weights(self):
        output_dict = {}
        for s in self.stock_arr:
            output_dict[s.ticker] = s['PriceClose'] * s['ShareIssued']
        marketcap_df = pd.DataFrame(output_dict).dropna()   
        weights_df = marketcap_df.apply(lambda x: normalize(x), axis = 1)
        return weights_df


    def generate_varcovar_mats(self, window=126):
        var_covar_ts = {}
        for i in range(len(self.returns_df)-window):
            dt = self.returns_df.index[i+window]
            ret_mat = self.returns_df.iloc[i:i+window, :]
            var_cov = ret_mat.cov() * 252
            # Apply shrinkage factor
            var_cov = var_cov * self.shrinkage_factor + \
                      (1.0-self.shrinkage_factor)*np.diag(np.diag(var_cov))
            var_covar_ts[dt] = var_cov
        return var_covar_ts

    def generate_inv_varcovar_mats(self):
        inv_var_covar_ts = deepcopy(self.var_covar_ts)
        for dt, var_cov_mat in self.var_covar_ts.items():
            inv_var_covar_ts[dt].loc[:, :] = inv(var_cov_mat)
        return inv_var_covar_ts
        

    def generate_implied_returns(self):
        implied_returns_dict = {}
        for dt, var_cov_mat in self.var_covar_ts.items():
            if dt in self.weights_shifted_df.index:
                
                weigts_arr = self.weights_shifted_df.loc[dt, :]            
                implied_returns_arr = self.A*var_cov_mat.dot(weigts_arr)            
                implied_returns_dict[dt] = implied_returns_arr
        implied_returns_df = pd.DataFrame(implied_returns_dict).T.dropna()
        return implied_returns_df
        

    def build_signal_df(self, signal_func):
        signal_dict = {}
        for stock_obj in self.stock_arr:
            stock_signal_ts = signal_func(stock_obj)
            stock_ticker = stock_obj.ticker
            signal_dict[stock_ticker] = stock_signal_ts
        signal_df = pd.DataFrame(signal_dict)
        return signal_df

    def generate_signal_ts_dict(self):
        dts = None
        for signal_label, signal_df in self.signal_df_dict.items():
            if dts is None:
                dts = signal_df.index
            else:
                dts = dts.intersection(signal_df.index)

        output_dict = {}
        for dt in dts:
            date_dict = {}
            for signal_label, signal_df in self.signal_df_dict.items():
                date_dict[signal_label] = signal_df.loc[dt, :]

            date_df = pd.DataFrame(date_dict).T
            output_dict[dt] = date_df
        return output_dict
        

    def generate_link_mats(self):
        link_mat_ts = {}
        for dt, signal_raw in self.signal_ts_dict.items():
            link_mat_ts[dt] = signal_raw.apply( lambda x: 2*((x.rank() - 1) / ( np.sum(~np.isnan(x)) - 1)) - 1, axis=1).fillna(0)
        return link_mat_ts

    def generate_view_var_covar_mats(self):
        view_var_covar_ts = {}
        for dt, var_cov_mat in self.var_covar_ts.items():
            if dt in self.link_mat_ts:
                P = self.link_mat_ts[dt]
                Sigma = self.var_covar_ts[dt]
                Omega = self.tau*P.dot(Sigma).dot(P.T)
                # Apply shrinkage factor
                Omega = Omega * self.shrinkage_factor + \
                          (1.0-self.shrinkage_factor)*np.diag(np.diag(Omega))               
                view_var_covar_ts[dt] = Omega
        return view_var_covar_ts


    def generate_view_inv_var_covar_mats(self):
        view_inv_var_covar_ts = deepcopy(self.view_var_covar_ts)
        for dt, view_var_cov_mat in self.view_var_covar_ts.items():
            view_inv_var_covar_ts[dt].loc[:, :] = inv(view_var_cov_mat)
        return view_inv_var_covar_ts        

    def generate_black_litterman_weights(self):
        black_litterman_weights_dict = {}
        for dt, view_inv_var_cov_mat in self.view_inv_var_covar_ts.items():
            if dt in self.implied_returns_df.index:
                black_litterman_weights_dict[dt] = self.tau*(self.inv_var_covar_ts[dt].dot(self.implied_returns_df.loc[dt])) \
                        + self.link_mat_ts[dt].T.dot(view_inv_var_cov_mat).dot(self.signal_view_ret_arr)
        black_litterman_weights_df = pd.DataFrame(black_litterman_weights_dict).T
        return black_litterman_weights_df


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
        
        
        
        
        
        
        
        
        
        
        






