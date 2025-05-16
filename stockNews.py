# Fetch current news articles about stocks from Financial Modeling Prep's API
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

# This decorator takes in fixed arguments on bounds for polarity and subjectivity
def GatherSentiment(lowerPOL, upperPOL, lowerSBJ, upperSBJ):
    # Generates the sentiment data
    def HandleSentiment(f):
        # Uses TextBlob to gain polarity (positive or negative sentiment) and subjectivity (fact or opinion)
        def SolveForIt(*a, **b):
            data = f(*a, **b)
            stocks = list(data.keys())
            
            # Counts for the number of positive and negative sentiment articles along with opinions and facts
            result = {stk:{'positive':0,'negative':0,'opinion':0,'fact':0} for stk in stocks}
            
            for ticker, paragraph in data.items():
                for sentence in paragraph:
                    ML = TextBlob(sentence).sentiment
                    POL = ML.polarity
                    SBJ = ML.subjectivity
                    if POL >= upperPOL:
                        result[ticker]['positive'] += 1
                    elif POL <= lowerPOL:
                        result[ticker]['negative'] += 1
                    else:
                        pass
                    if SBJ >= upperSBJ:
                        result[ticker]['fact'] += 1
                    elif SBJ <= lowerSBJ:
                        result[ticker]['opinion'] += 1
            return result
        return SolveForIt
    return HandleSentiment

# This decorator utilizes BeautufulSoup to extract text from the inputted html code returned by the API
def ExtractFromHTML(f):
    def ProblemSolution(*a, **b):
        tickers, stocks, result = f(*a, **b)
        data = {stk:[] for stk in stocks}
        for stock, article in zip(stocks, result):
            soup = BeautifulSoup(article, 'html.parser')
            
            # Pulls paragraphs
            data[stock] += [u.get_text() for u in soup.find_all('p')]
        return data
    return ProblemSolution

# This decorator builds a pandas dataframe with all of the positive and negative sentiment
def CreateDataFrame(f):
    def Solve(*a, **b):
        z = f(*a, **b)
        final_result = []
        stocks = list(z.keys())
        for i in stocks:
            final_result.append(z[i])
        df = pd.DataFrame(final_result, index=stocks)
        return df
    return Solve

# Three decorators are used to take the news data and successfully parse it into a Pandas dataframe
@CreateDataFrame
@GatherSentiment(-0.45, 0.45, 0.2, 0.8)
@ExtractFromHTML
def FetchData(pages, size):
    # Extracts the tickers
    def CutTicks(x):
        if ':' in x:
            x = x.split(':')[1]
            return x
        return x
    result = []
    stocks = []
    # Sifts through a set number of news pages
    for page in range(pages):
        print("Fetching page number ", page)

        # Fetches the news articles
        url = FMPNews(page=page, size=size)

        # Pulls the tickers and content
        resp = requests.get(url).json()
        resp = resp['content']
        stocks += [CutTicks(t['tickers']) for t in resp]
        result += [t['content'] for t in resp]
        time.sleep(0.7)
        
    tickers = list(set(stocks))
    return tickers, stocks, result

# Sets pages equal to 1 with 500 articles in them
pages = 1
size = 500

# Fetches the sentiment dataframe
sentiment = FetchData(pages, size)

# Sorts the dataframe by number of positive articles on each stock
sentiment = sentiment.sort_values(by='positive', ascending=False)

import matplotlib.pyplot as plt

# Plots a scatterplot between the opinion and fact values
x = sentiment['opinion'].values
y = sentiment['fact'].values

plt.scatter(x, y, color='red')
plt.show()
