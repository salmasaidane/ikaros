# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 14:41:34 2021

@author: saidsa
"""

import pandas_datareader.data as web  # module for reading datasets directly from the web
from datetime import datetime
import os
from Utils import pandas_csv_cache


if os.getenv("IKAROSDATA") is not None:
    library_folder = os.getenv("IKAROSDATA")
else:
    library_folder = os.path.join(os.getenv("APPDATA"), "IKAROSDATA")
    if not os.path.isdir(library_folder):
        os.mkdir(library_folder)
        
        
@pandas_csv_cache(folder=os.path.join(library_folder, 'FamaFrench'),
                  file_template='FamaFrench_Data.csv',
                  expiration_in_sec=24*60*60,
                  read_csv_kwargs={'sep': '|',
                                   'parse_dates': [0],
                                   'index_col': 0 },
                  to_csv_kwargs={'index': True,
                                 'sep': '|'})
def get_Fama_French_df():
    F_F_Dataset_Name = 'F-F_Research_Data_Factors_daily'
    F_F_Data = web.DataReader(F_F_Dataset_Name,'famafrench', 
                              start='2000-01-01', 
                              end=datetime.today().strftime('%Y-%m-%d')) 
    F_F_df = F_F_Data[0].dropna() / 100 # Scaling data from % to decimal to line up data with returns data
    F_F_df.index = F_F_df.index.map(lambda x: x.date())
    return F_F_df
 
    
def get_Fama_French_ts(series_name):
    F_F_df = get_Fama_French_df()
    F_F_series = F_F_df[series_name]
    return F_F_series
 

 
    
 
    
 
    
 
    
 
    
 
    