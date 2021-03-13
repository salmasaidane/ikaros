# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 14:45:14 2021

@author: saidsa
"""

import os
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.support.ui import Select
import time
from yahooquery import Ticker    
from textblob import TextBlob
from Utils import as_of_date_to_quarter
from Utils import pandas_csv_cache

if os.getenv("IKAROSDATA") is not None:
    library_folder = os.getenv("IKAROSDATA")
else:
    library_folder = os.path.join(os.getenv("APPDATA"), "IKAROSDATA")
    if not os.path.isdir(library_folder):
        os.mkdir(library_folder)



@pandas_csv_cache(folder=os.path.join(library_folder, 'ZacksEarningsCalendar'),
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
    select = Select(driver.find_element_by_name('earnings_announcements_earnings_table_length'))
    select.select_by_visible_text('100')
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


@pandas_csv_cache(folder=os.path.join(library_folder, 'FinvizFundamentalRatings'),
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
        try:    
            Old_PT = float(Old_PT.strip().replace('$',''))
            New_PT = float(New_PT.strip().replace('$',''))
        except ValueError:
            Old_PT = np.NaN
            New_PT = np.NaN
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



@pandas_csv_cache(folder=os.path.join(library_folder, 'FinvizInsiderTrading'),
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

@pandas_csv_cache(folder=os.path.join(library_folder, 'FinvizNews'),
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
    
    def __init__(self, ticker, fundamental_frequency='q'):
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
        self.financial_data = self.get_all_financial_data(fundamental_frequency=fundamental_frequency)
        try:
            self.ratings_data = get_finviz_fundamentals_ratings(ticker)
        except:
            self.ratings_data = None
        try:
            self.insider_trading_data = get_finviz_inside_trading(ticker)
        except:
            self.insider_trading_data = None
        try:
            self.news_data = get_finviz_news(ticker)
        except:
            self.news_data = None
            
            
    def get_all_financial_data (self, fundamental_frequency='q'):
        df = self.yquery.all_financial_data( frequency = fundamental_frequency)
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
            

    

        
        
        
        