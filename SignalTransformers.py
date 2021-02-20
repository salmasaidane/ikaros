# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 20:14:04 2021

@author: saidsa
"""

def Z_Score(signal_ts, window = 21):
    return signal_ts.rolling(window = window).apply(lambda x: (x[-1] - x[0:-1].mean()) / x[0:-1].std())
 