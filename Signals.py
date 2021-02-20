# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 13:55:33 2021

@author: saidsa
"""

import numpy as np
import pandas as pd

######################### Valuation Ratios ###################################
def Price_to_Sales_Signal (stock_object):
    return stock_object['PriceClose'] / (stock_object['TotalRevenue'] /stock_object['ShareIssued'])
    

def Price_to_Earnings_Signal (stock_object):
    return stock_object['PriceClose'] / (stock_object['NetIncomeCommonStockholders'] /stock_object['ShareIssued'])

def Price_to_CashFlow_Signal (stock_object):
    return stock_object['PriceClose'] / (stock_object['FreeCashFlow'] /stock_object['ShareIssued'])

def Price_to_Book_Signal (stock_object):
    return stock_object['PriceClose'] / (stock_object['CommonStockEquity'] /stock_object['ShareIssued'])

def DividendPayout_Ratio_Signal (stock_object):
    return stock_object['CashDividendsPaid'] / stock_object['NetIncomeCommonStockholders']

def RetentionRate_Signal (stock_object):
    DP = DividendPayout_Ratio_Signal (stock_object)
    return 1 - DP

def SustainableGrowth_Signal (stock_object):
    RR= RetentionRate_Signal(stock_object)
    ROE = ReturnOnEquity_Signal(stock_object)
    return RR * ROE



########################## Activity Ratios ####################################


def DaysInventoryOutstanding_Signal(stock_object):
    return (stock_object['Inventory'] + 0.5*stock_object['ChangeInInventory']) \
                    / ( stock_object['CostOfRevenue'] / 365.0)

def DaysSalesOutstanding_Signal(stock_object):
    return (stock_object['AccountsReceivable'] + 0.5*stock_object['ChangesInAccountReceivables']) \
                    / ( stock_object['TotalRevenue'] / 365.0)


def DaysPayableOutstanding_Signal(stock_object):
    return (stock_object['AccountsPayable'] + 0.5*stock_object['ChangeInAccountPayable']) \
                    / ( stock_object['CostOfRevenue'] / 365.0)

def WorkingCapitalTurnover_Signal(stock_object):
    return stock_object['TotalRevenue'] / stock_object['WorkingCapital']

def FixedAssetsTurnover_Signal(stock_object):
    return stock_object['TotalRevenue'] / (stock_object['TotalAssets'] - stock_object['GoodwillAndOtherIntangibleAssets'])

def TotalAssetsTurnover_Signal(stock_object):
    return stock_object['TotalRevenue'] / stock_object['TotalAssets']


######################### Liquidity Ratios ###################################
def Current_Ratio_Signal(stock_object):
    return stock_object['CurrentAssets'] / stock_object['CurrentLiabilities']

def Quick_Ratio_Signal(stock_object):
    return (stock_object['CurrentAssets'] - stock_object['Inventory'])\
            / stock_object['CurrentLiabilities']

def Cash_Ratio_Signal(stock_object):
    return stock_object['CashAndCashEquivalents'] / stock_object['CurrentLiabilities']

def DefensiveInterval_Ratio_Signal(stock_object):
    return (stock_object['CashAndCashEquivalents'] + stock_object['Receivables']) \
            / stock_object['CurrentLiabilities']

def CashConverstionCycle_Signal(stock_object):
    DIO = DaysInventoryOutstanding_Signal(stock_object)
    DSO = DaysSalesOutstanding_Signal(stock_object)
    DPO = DaysPayableOutstanding_Signal(stock_object)
    return DIO + DSO - DPO


######################## Profitability Ratios ##################################

def GrossProfitMargin_Signal(stock_object):
    return stock_object['GrossProfit'] / stock_object['TotalRevenue']

def OperatingProfitMargin_Signal(stock_object):
    return stock_object['OperatingIncome'] / stock_object['TotalRevenue']

def PreTaxMargin_Signal(stock_object):
    return (stock_object['EBIT'] - stock_object['InterestExpense']) / stock_object['TotalRevenue']

def NetIncomeMargin_Signal(stock_object):
    return stock_object['NetIncome'] / stock_object['TotalRevenue']


def ReturnOnAssets_Signal(stock_object):
    return stock_object['NetIncome'] / stock_object['TotalAssets']

def OperatingReturnOnAssets_Signal(stock_object):
    return stock_object['OperatingIncome'] / stock_object['TotalAssets']


def ReturnOnEquity_Signal(stock_object):
    return stock_object['NetIncome'] / stock_object['TotalEquityGrossMinorityInterest']

def OperatingReturnOnEquity_Signal(stock_object):
    return stock_object['OperatingIncome'] / stock_object['TotalEquityGrossMinorityInterest']

def ReturnOnCommonEquity_Signal(stock_object):
    return stock_object['DilutedNIAvailtoComStockholders'] / stock_object['CommonStockEquity']



######################### Solvency Ratios ###################################

def Debt_to_Assets_Signal(stock_object):
    return stock_object['TotalDebt'] / stock_object['TotalAssets']


def Debt_to_Capital_Signal(stock_object):
    return stock_object['TotalDebt'] / ( stock_object['TotalDebt'] + stock_object['TotalEquityGrossMinorityInterest'] )

def Debt_to_Equity_Signal(stock_object):
    return stock_object['TotalDebt'] / stock_object['TotalEquityGrossMinorityInterest']

def FinancialLeverage_Signal(stock_object):
    return stock_object['TotalAssets'] / stock_object['TotalEquityGrossMinorityInterest']

def InterestCoverage_Signal(stock_object):
    return stock_object['EBIT'] / stock_object['InterestExpense']

def FixedCharge_Signal(stock_object):
    return ( stock_object['EBIT'] + stock_object['Leases'] ) / \
                 ( stock_object['InterestExpense'] + stock_object['Leases'] )


########################### Insider Flow #####################################

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

########################### Price Target ##################################### 

def Price_target_to_Price_Signal(stock_obj):
    ratings_df = stock_obj.ratings_data
    ratings_df['DateTime'] =  pd.to_datetime(ratings_df['RatingDate'])
    PT_ts = ratings_df.set_index('DateTime').loc[:, 'NewPT'].resample('D').mean()
    PT_ts.index = PT_ts.index.map(lambda x: x.date())
    PT_ts = PT_ts.reindex(stock_obj['PriceClose'].index).ffill()
    signal_ts = (PT_ts - stock_obj['PriceClose']) / stock_obj['PriceClose']
    return signal_ts
    

