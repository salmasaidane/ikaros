# -*- coding: utf-8 -*-
"""
Created on Sun May  2 14:45:13 2021

@author: saidsa
"""

from MacroData import get_Fama_French_ts
from Utils import OLS_regression
from Utils import align_date_index
from MacroData import get_Fama_French_Mkt_Return
import numpy as np
import pandas as pd


def _DEP_CAPM(stock_obj):
    
    # Run OLS regression of stock returns against Fama French Rm-Rf => returns 
    # a value for beta of your stock, and a ts of epsilon
    # Use epsilon ts to get var of epsilon (value)
    # Get fama french Rf, Rm-Rf and Rm, compute avg and var of these
    # CAPM => Stock_Exp_Ret  and  Stock_Exp_Var 
    
    
    stock_returns = stock_obj['PriceClose'].pct_change(1).dropna()
    Mkt_Rf_Return_ts = get_Fama_French_ts('Mkt-RF')
    Mkt_Rf_Return_ts.index = Mkt_Rf_Return_ts.index.map(lambda x: x.date())
    X, Y = align_date_index(obj_1=Mkt_Rf_Return_ts.to_frame(), obj_2=stock_returns)
    regression_dict =  OLS_regression(X=X ,Y=Y , add_constant=True)
    beta_stock = regression_dict['Beta_hat']['Mkt-RF']
    var_epsilon_stock = regression_dict['Epsilon_hat'].var()
    
    Mkt_Return_ts = get_Fama_French_Mkt_Return()
    Rf_Return_ts = get_Fama_French_ts('RF')
    
    Mkt_Avg_Return = Mkt_Return_ts.mean()
    Mkt_Var_Return = Mkt_Return_ts.var()
    Rf_Avg_Return = Rf_Return_ts.mean()
    
    Stock_Expected_return = Rf_Avg_Return + (Mkt_Avg_Return - Rf_Avg_Return) * beta_stock
    Stock_Expected_var = Mkt_Var_Return * (beta_stock ** 2) + var_epsilon_stock
    return Stock_Expected_return, Stock_Expected_var
    
    
    
    
    
    
def CAPM(stock_obj_arr, window = 126):
    
    # Given a stock_obj_arr, we get returns of these stocks
    # We align index ts
    # We use the Rf as a constant over the regression window
    # We assume expected value of market returns as a simple avg over the regression
    # window. We assume the same for market_var
    # We run a rolling regression for every stock to get its market betas and 
    # idiosyncratic risk. Finally we construct the CAPM model to get the:
    # Expected returns
    # VAR_COVAR matrix
    # Systematic and Idiosyncratic VARCOVAR matrix
    
    Mkt_Rf_Return_ts = get_Fama_French_ts('Mkt-RF')
    Mkt_Rf_Return_ts.index = Mkt_Rf_Return_ts.index.map(lambda x: x.date())
    Mkt_Return_ts = get_Fama_French_Mkt_Return()
    Mkt_Return_ts.index = Mkt_Return_ts.index.map(lambda x: x.date())
    Rf_Return_ts = get_Fama_French_ts('RF')
    Rf_Return_ts.index = Rf_Return_ts.index.map(lambda x: x.date())
    arr = [Mkt_Rf_Return_ts, Mkt_Return_ts, Rf_Return_ts]
    for obj in stock_obj_arr:
        stock_returns = obj['PriceClose'].pct_change(1).dropna()
        arr.append(stock_returns)
    aligned_arr = align_date_index(arr)

    # Window loop
    
    total_observations = len(aligned_arr[0])
    nbr_regressions = total_observations - window
    
    stock_labels = [obj.ticker for obj in stock_obj_arr]
    regression_output_dates = aligned_arr[0].index[window:]
    Expected_Returns_df = pd.DataFrame(columns=stock_labels, index=regression_output_dates)
    Covar_Returns_dict = {dt: pd.DataFrame(index=stock_labels, columns=stock_labels) for dt in regression_output_dates}
    Sys_Covar_Returns_dict = {dt: pd.DataFrame(index=stock_labels, columns=stock_labels) for dt in regression_output_dates}
    Idio_Covar_Returns_dict = {dt: pd.DataFrame(index=stock_labels, columns=stock_labels) for dt in regression_output_dates}
    
    
    for i in range (nbr_regressions):
        dt = regression_output_dates[i]
        X = aligned_arr[0].iloc[i:i+window].to_frame()
        Rf = aligned_arr[2].iloc[i:i+window].mean()
        mu_m = aligned_arr[1].iloc[i:i+window].mean() 
        var_m = aligned_arr[1].iloc[i:i+window].var()
        
        beta_arr = []
        var_epsilon_arr = []
        
        
        for stock_ret in aligned_arr[3:]:
            Y = stock_ret.iloc[i:i+window]
            
            regression_dict =  OLS_regression(X=X ,Y=Y , add_constant=True)
            beta_stock = regression_dict['Beta_hat']['Mkt-RF']
            var_epsilon_stock = regression_dict['Epsilon_hat'].var()
            
            beta_arr.append(beta_stock)
            var_epsilon_arr.append(var_epsilon_stock)
            
        Expected_Returns_arr = Rf + (mu_m - Rf) * np.array(beta_arr)
        Covar_Returns_mat = var_m * (np.matrix(beta_arr).T.dot(np.matrix(beta_arr))) + np.diag(var_epsilon_arr)
        Sys_Covar_Returns_mat = var_m * (np.matrix(beta_arr).T.dot(np.matrix(beta_arr)))
        Idio_Covar_Returns_mat = np.diag(var_epsilon_arr)
        
        
        Expected_Returns_df.loc[dt, :] = Expected_Returns_arr * 252
        Covar_Returns_dict[dt].loc[:,:]= Covar_Returns_mat * 252
        Sys_Covar_Returns_dict[dt].loc[:,:]= Sys_Covar_Returns_mat * 252
        Idio_Covar_Returns_dict[dt].loc[:,:]= Idio_Covar_Returns_mat * 252
                
    return Expected_Returns_df, Covar_Returns_dict, Sys_Covar_Returns_dict, Idio_Covar_Returns_dict
            
        
        
        

    
    
    
    
    