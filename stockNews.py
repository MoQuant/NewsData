def FMPNews(page=0, size=5):
    key = ''
    return f'https://financialmodelingprep.com/api/v3/fmp/articles?page={page}&size={size}&apikey={key}'

import requests
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from textblob import TextBlob 
import time 

# Display all rows
pd.set_option('display.max_rows', None)

# Display all columns
pd.set_option('display.max_columns', None)

def CleanHTML(f):
    def Solve(*a, **b):
        data = f(*a, **b)
        result = {}
        for stock, article in data.items():
            for story in article:
                soup = BeautifulSoup(story, 'html.parser')
                sentences = [p.get_text() for p in soup.find_all("p")][1:]
            result[stock] = sentences
        return result
    return Solve

def Extract(f):
    def Solve(*a, **b):
        stocks, tickers, news = f(*a, **b)
        data = {tick:[] for tick in stocks}
        for ticker, article in zip(tickers, news):
            data[ticker].append(article)
        return data
    return Solve

def DataFrame(f):
    def Handle(*a, **b):
        Y = f(*a, **b)
        data = []
        indexs = []
        for i in Y:
            indexs.append(i)
            data.append(Y[i])
        return pd.DataFrame(data, index=indexs)
    return Handle

class Data:

    def __init__(self):
        self.session = requests.Session()

    def fetchData(self, page=0, size=3):
        print(f"Fetching Page: {page} with a size of {size}")
        resp = self.session.get(FMPNews(page=page, size=size)).json()
        df = pd.DataFrame(resp['content'])
        time.sleep(1)
        return df
    
    @CleanHTML
    @Extract
    def extractData(self, df):
        def parseTicks(tick):
            try:
                answer =tick.split(':')[1]
            except:
                answer = tick
            return answer
        tickers = list(map(parseTicks, df['tickers'].values.tolist()))
        news = df['content'].values.tolist()
        stocks = list(set(tickers))
        return stocks, tickers, news
    
    @DataFrame
    def classifyNewsSentiment(self, newsData):
        scores = []
        tickers = list(newsData.keys())
        count = {tick:{'positive':0,'negative':0,'opinion':0,'fact':0} for tick in tickers}
        for ticker, article in newsData.items():
            for sentence in article:
                analyze = TextBlob(sentence).sentiment
                polarity = analyze.polarity
                subjective = analyze.subjectivity
                
                if subjective >= 0.75:
                    count[ticker]['fact'] += 1
                elif subjective <= 0.25:
                    count[ticker]['opinion'] += 1
                else:
                    pass 
                
                if polarity >= 0.4:
                    count[ticker]['positive'] += 1
                elif polarity <= -0.4:
                    count[ticker]['negative'] += 1
                else:
                    pass
        return count
                
            

pages = (0, 1, 2, 3, 4)

finalSet = []

client = Data()
for page in pages:
    df = client.fetchData(page=page, size=30)
    newsData = client.extractData(df)
    sentiment = client.classifyNewsSentiment(newsData)
    if page == 0:
        finalSet = sentiment
    else:
        finalSet = pd.concat([finalSet, sentiment], ignore_index=False)

print(finalSet)



