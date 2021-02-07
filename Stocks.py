# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 14:45:14 2021

@author: saidsa
"""

import os
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager 
import time
from yahooquery import Ticker    
import functools
from numpy.linalg import inv
from textblob import TextBlob


def as_of_date_to_quarter (dt):
    month, year = dt.month, dt.year
    Q = int((int(month) - 0.01)/ 3) + 1
    return str(Q)+'Q'+ str(year)

def normalize (x):
    x[x>0.001] = x[x>0.001] / x[x>0.001].sum()
    x[x<0.001] = x[x<0.001] / - x[x<0.001].sum()
    return x

def pandas_csv_cache(folder, file_template, expiration_in_sec,
                     read_csv_kwargs={'sep', '|'}, to_csv_kwargs={'sep': '|'}):
    def decorator_pandas_csv_cache(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ticker = kwargs['ticker'] if 'ticker' in kwargs else args[0]
            file_path = os.path.join(folder, file_template.format(ticker=ticker))
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


@pandas_csv_cache(folder=r'C:\Users\youss\Desktop\Python study Trello Board\Session 8 - Quant Library\ZacksEarningsCalendar',
                  file_template='{ticker}.csv',
                  expiration_in_sec=24*60*60*15,
                  read_csv_kwargs={'sep': '|',
                                   'parse_dates': [0]},
                  to_csv_kwargs={'index': False,
                                 'sep': '|'})
def get_zacks_earnings_calendar(ticker):
    
    url = 'https://www.zacks.com/stock/research/{ticker}/earnings-announcements'.format(ticker=ticker)
    
    opts = Options()     
    opts.headless = True
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser') 
    driver.close()
    
    table = soup.find('table', id='earnings_announcements_earnings_table')
    table_body = table.find('tbody')
    
    rows = table_body.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        Q , Y = cols[1].text.split('/') 
        Q = int((int(Q) - 0.01)/ 3) + 1
        RelaseDate = datetime.strptime(cols[0].text, '%m/%d/%Y').date()
        data.append(
        {
            'ReleaseDate': RelaseDate,
            'Quarter': str(Q)+'Q'+Y,
            })
        
    df = pd.DataFrame(data)
    return df


@pandas_csv_cache(folder=r'C:\Users\youss\Desktop\Python study Trello Board\Session 8 - Quant Library\FinvizFundamentalRatings',
                  file_template='{ticker}.csv',
                  expiration_in_sec=24*60*60*15,
                  read_csv_kwargs={'sep': '|',
                                   'parse_dates': [0]},
                  to_csv_kwargs={'index': False,
                                 'sep': '|'})
def get_finviz_fundamentals_ratings(ticker):
    
    url = 'https://finviz.com/quote.ashx?t={ticker}'.format(ticker=ticker)
    
    opts = Options()     
    opts.headless = True
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser') 
    driver.close()
    
    
    table = soup.find('table', attrs={'class':'fullview-ratings-outer'})
    table_body = table.find('tbody')
    
    rows = table_body.find_all('tr')
    data = []
    for row in rows:
        if row.find('table') is not None:
            cols = row.find('td').find('table').find('tbody').find('tr').find_all('td')
        else:
            cols = row.find_all('td')
        Rating_Date = datetime.strptime(cols[0].text, '%b-%d-%y').date()
        Rating_Change = cols[1].text
        Company = cols[2].text
        
        
        if '→' in cols[3].text:
            Old_Rating, New_Rating = cols[3].text.split('→')
        else:
            Old_Rating = cols[3].text
            New_Rating = cols[3].text
        
        if '→' in cols[4].text:
            Old_PT, New_PT = cols[4].text.split('→')
        else:
            Old_PT = cols[4].text
            New_PT = cols[4].text
            
        Old_PT = float(Old_PT.strip().replace('$',''))
        New_PT = float(New_PT.strip().replace('$',''))
        data.append(
        {
            'RatingDate': Rating_Date,
            'RatingChange': Rating_Change,
            'Company': Company,
            'OldRating': Old_Rating,
            'NewRating': New_Rating,
            'OldPT': Old_PT,
            'NewPT': New_PT
            })
        
    df = pd.DataFrame(data).drop_duplicates()
    return df



@pandas_csv_cache(folder=r'C:\Users\youss\Desktop\Python study Trello Board\Session 8 - Quant Library\FinvizInsiderTrading',
                  file_template='{ticker}.csv',
                  expiration_in_sec=24*60*60*15,
                  read_csv_kwargs={'sep': '|',
                                   'parse_dates': [0]},
                  to_csv_kwargs={'index': False,
                                 'sep': '|'})
def get_finviz_inside_trading(ticker):
    
    today = datetime.now().date()
    url = 'https://finviz.com/quote.ashx?t={ticker}'.format(ticker=ticker)
    
    opts = Options()     
    opts.headless = True
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser') 
    driver.close()
    
    
    table = soup.find('table', attrs={'class':'body-table', 'bgcolor':'#d3d3d3'})
    table_body = table.find('tbody')
    
    rows = table_body.find_all('tr')
    data = []
    for row in rows[1:]:
        cols = row.find_all('td')
        InsiderName = cols[0].text
        Relationship = cols[1].text
        
        Temp_Date = cols[2].text
        Conv_Date_date = datetime.strptime(Temp_Date + ' ' + str(today.year), '%b %d %Y').date()
        if Conv_Date_date > today:
            Conv_Date_date = datetime.strptime(Temp_Date + ' ' + str(today.year - 1), '%b %d %Y').date()
    
        Transaction = cols[3].text
        Cost = float(cols[4].text.replace(',',''))
        NumberShares = int(cols[5].text.replace(',',''))
        Value = float(cols[6].text.replace(',',''))
        NumberTotalShares = int(cols[7].text.replace(',',''))
        SEC_Form4 = cols[8].find('a')['href']
        
        data.append(
        {
            'Date': Conv_Date_date,
            'InsiderName': InsiderName,
            'Relationship': Relationship,
            'Transaction': Transaction,
            'Cost': Cost,
            'NumberShares': NumberShares,
            'Value': Value,
            'NumberTotalShares': NumberTotalShares,
            'SEC_Form4': SEC_Form4
            })
        
    df = pd.DataFrame(data)
    return df

@pandas_csv_cache(folder=r'C:\Users\youss\Desktop\Python study Trello Board\Session 8 - Quant Library\FinvizNews',
                  file_template='{ticker}.csv',
                  expiration_in_sec=24*60*60*1,
                  read_csv_kwargs={'sep': '|',
                                   'parse_dates': [0]},
                  to_csv_kwargs={'index': False,
                                 'sep': '|'})
def get_finviz_news(ticker):
    
    url = 'https://finviz.com/quote.ashx?t={ticker}'.format(ticker=ticker)
    
    opts = Options()     
    opts.headless = True
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser') 
    driver.close()
    
    
    table = soup.find('table', id='news-table')
    table_body = table.find('tbody')
    
    rows = table_body.find_all('tr')
    data = []
    date_info = None

    for row in rows:
        cols = row.find_all('td')
        Temp_Date = cols[0].text 
        Temp_Date = Temp_Date.replace('\xa0','').strip()
        if len(Temp_Date.split(' ')) == 2: #Table always starts with a date info
            date_info, time_info = Temp_Date.split(' ')
        else:
            time_info = Temp_Date
        News_Date_Time = datetime.strptime(date_info + ' ' + time_info, '%b-%d-%y %I:%M%p')
        News_info = cols[1].find('div', attrs = {'class': 'news-link-container'})\
                            .find('div', attrs = {'class': 'news-link-left'})\
                            .find('a', attrs = {'class': 'tab-link-news'})
        #Rating_Date = datetime.strptime(cols[0].text, '%b-%d-%y').date()
        News_headlines = News_info.text
        News_link = News_info['href']
        News_publication = cols[1].find('div', attrs = {'class': 'news-link-container'})\
                            .find('div', attrs = {'class': 'news-link-right'}).text
        data.append(
        {
            'NewsDateTime': News_Date_Time,
            'NewsHeadlines': News_headlines,
            'Newslink': News_link,
            'NewsPublication': News_publication,
            'NewsSentiment': TextBlob(News_headlines).sentiment.polarity ,
            'NewsSubjectivity': TextBlob(News_headlines).sentiment.subjectivity
            })
        
    df = pd.DataFrame(data)
    return df



class Stock(object):
    
    def __init__(self, ticker):
        self.ticker= ticker
        self.zacks_earnings_cal = get_zacks_earnings_calendar(ticker)
        self.yquery = Ticker(ticker)
        self.returns_data = self.yquery.history(adj_ohlc=True,  
                                 start=(datetime.today() \
                                        -timedelta(days = 365*3)
                                        ).strftime('%Y-%m-%d'), 
                                 end = datetime.today().strftime('%Y-%m-%d')
                                 ).droplevel(0).rename(columns={'high': 'PriceHigh',
                                                                'volume': 'Volume',
                                                                'open': 'PriceOpen',
                                                                'low': 'PriceLow',
                                                                'close': 'PriceClose' 
                                                                })
        self.financial_data = self.get_all_financial_data()
        self.ratings_data = get_finviz_fundamentals_ratings(ticker)
        self.insider_trading_data = get_finviz_inside_trading(ticker)
        self.news_data = get_finviz_news(ticker)
        
    def get_all_financial_data (self):
        df = self.yquery.all_financial_data( frequency = 'q')
        df['Quarter'] = df['asOfDate'].apply(lambda x: as_of_date_to_quarter(x))
        df = pd.merge(df, self.zacks_earnings_cal, how = 'left', on = 'Quarter')\
            .set_index('ReleaseDate').drop(['asOfDate', 'periodType', 'Quarter'], axis = 1)
        return df
        
        
        
    def get_fundamental_ts (self, item):
        ts = self.financial_data[item]
        date_idx = pd.date_range(self.returns_data.index[0], self.returns_data.index[-1])
        ts = ts.reindex(index = date_idx).shift(1).ffill()
        ts = ts.loc[self.returns_data.index]
        return ts
        
    def __getitem__(self, item):
        if item in self.returns_data.columns:
            return self.returns_data[item]
        elif item in self.financial_data.columns:
            return self.get_fundamental_ts(item)
        else:
            raise KeyError('Item not Found!')
            

def Price_to_Sales_Signal (stock_object, raw = True, window = 21):
    if raw:
        return stock_object['PriceClose'] / stock_object['TotalRevenue']
    else:
        return (stock_object['PriceClose'] / stock_object['TotalRevenue']).rolling(window = window).apply(lambda x: (x[-1] - x.mean())/(x.std()))
      
        
      
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
    
'''   
def Price_to_Earnings (stock_object, raw = True, window = 21):
    if raw:
        return stock_object['PriceClose'] / stock_object['RetainedEarnings']
    else:
        return (stock_object['PriceClose'] / stock_object['RetainedEarnings']).rolling(window = window).apply(lambda x: (x[-1] - x.mean())/(x.std()))
 #Condition on PE within a range, else return 0
 #Column PeRatio in dataset
    
def quick_ratio():
    return 


    
def altman_Z_Score():
    return -1

'''    
    
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
        

        
        
        
        