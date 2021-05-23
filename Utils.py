# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 15:02:32 2021

"""
from numpy.linalg import inv
import pandas as pd
import functools
import os
import time

def OLS_regression(X,Y, add_constant = True):
    
    if add_constant:
        X['Constant'] = 1
        
    n = len(Y)
    k = len(X.columns)

    Beta_hat = pd.Series(data = inv(X.T.dot(X)).dot(X.T.dot(Y)), index = X.columns )
    
    Y_hat = X.dot(Beta_hat)
    
    Epsilon_hat = Y - Y_hat
    
    Sigma_hat_square = sum(Epsilon_hat ** 2) / (n - k)
    
    Var_Beta_hat_hat = Sigma_hat_square * inv(X.T.dot(X))
    
    Std_err_Beta_hat = pd.Series(Var_Beta_hat_hat.diagonal() ** 0.5, index = X.columns)
    
    t_stat_Beta_hat = Beta_hat / Std_err_Beta_hat

    return {'Beta_hat': Beta_hat,
            'Y_hat': Y_hat,
            'Epsilon_hat': Epsilon_hat,
            'Sigma_hat_square': Sigma_hat_square,
            'Var_Beta_hat_hat': Var_Beta_hat_hat,
            'Std_err_Beta_hat': Std_err_Beta_hat,
            't_stat_Beta_hat': t_stat_Beta_hat
            }


def as_of_date_to_quarter (dt):
    month, year = dt.month, dt.year
    Q = int((int(month) - 0.01)/ 3) + 1
    return str(Q)+'Q'+ str(year)

def pandas_csv_cache(folder, file_template, expiration_in_sec,
                     read_csv_kwargs={'sep', '|'}, to_csv_kwargs={'sep': '|'}):
    def decorator_pandas_csv_cache(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not os.path.isdir(folder):
                os.mkdir(folder)
            if '{ticker}' in file_template:
                ticker = kwargs['ticker'] if 'ticker' in kwargs else args[0]
                file_path = os.path.join(folder, file_template.format(ticker=ticker))
            else:
                file_path = os.path.join(folder, file_template)
            if os.path.isfile(file_path):
                if time.time() - os.path.getmtime(file_path) <= expiration_in_sec:
                    return pd.read_csv(file_path, **read_csv_kwargs)
                else:
                    os.remove(file_path)
            df = func(*args, **kwargs)
            df.to_csv(file_path, **to_csv_kwargs)
            return df
        return wrapper
    return decorator_pandas_csv_cache


def Rolling_Regression( Y_ts, X_ts_arr, window=42):
    input_dict = {}
    X_cols = []
    output_dict = {}
    if type(Y_ts.index[0]) == pd._libs.tslibs.timestamps.Timestamp:
        Y_ts.index = Y_ts.index.map(lambda x: x.date())
    for ts in X_ts_arr:
        if type(ts.index[0]) == pd._libs.tslibs.timestamps.Timestamp:
            ts.index = ts.index.map(lambda x: x.date())
        input_dict[ts.name] = ts
        X_cols.append(ts.name)
              
    input_dict[Y_ts.name] = Y_ts
    input_df = pd.DataFrame(input_dict).dropna()
    input_df['Constant'] = 1
    X_cols.append('Constant')
    total_observations = len(input_df)
    nbr_regressions = total_observations - window
    
    for i in range (nbr_regressions):
        output_date = input_df.index[i+window]
        run_date_index = input_df.index[i:i+window]
        Y = input_df.loc[run_date_index, Y_ts.name]
        X = input_df.loc[run_date_index, X_cols]
        output_dict[output_date] = OLS_regression(X,Y, add_constant = False)
    return output_dict


def _DEP_align_date_index(obj_1, obj_2):
    idx = obj_1.index.intersection(obj_2.index)
    return obj_1.loc[idx], obj_2.loc[idx]
    

def align_date_index(obj_arr):
    # build index intersection of all objects
    # Use index to filter all objects
    idx = None
    for obj in obj_arr:
        if idx is None:
            idx = obj.index
        else:
            idx = idx.intersection(obj.index)
    return [obj.loc[idx] for obj in obj_arr]
    







            
            
            
            
            
            
            
            
            