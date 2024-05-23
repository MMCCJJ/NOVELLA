import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import time
import pytrends
import numpy as np

CATEGORIA_TODAS = 0
CATEGORIA_LIBROS = 22

def getInterestOverTime(keywords, categoria, tf):
    """Devuelve datos relacionados con el interés a lo largo del tiempo
    de la lista de keywords introducidas en una categoría y un timeframe dados"""
    try:
        pytrends.build_payload(keywords, cat=categoria, timeframe=tf) 
        data = pytrends.interest_over_time() 
        data = data.reset_index()
        return data
    except Exception as e:
        print(e)

    return pd.DataFrame()

def getAdvancedKeyword(kw):
    """Obtiene la keyword codificada dado un título"""

    suggestions = pytrends.suggestions(keyword=kw)
    book = next((item for item in suggestions if 'Book' in item['type']), None)
    if book != None:
        return book['mid']
    return kw


def getTrends(df, maxCount = 5000):
    """Dado un dataframe de bestsellers, obtiene el interés para cada libro y autor si BookInterest1M es 0"""
    

    while True:
        countTotal = 0
        countBuenos = 0
        countMalos = 0
        for i, row in df.iterrows():

            if row['BookInterest1M'] == 0:
                book = row['Title']
                keywordsBook = [book]
                date = row['Date']
                minusMonth = date - timedelta(days=30)
                tfM = minusMonth.strftime("%Y-%m-%d") + " " + date.strftime("%Y-%m-%d")

                data = getInterestOverTime(keywordsBook, CATEGORIA_LIBROS, tfM)
                try:
                    suma = sum(data[book])
                    print("Suma = ", suma)
                    df.at[i, 'BookInterest1M'] = suma
                    countBuenos += 1
                    countMalos = 0
        
                except KeyError as e:
                    df.at[i, 'BookInterest1M'] = np.nan
                    countMalos += 1

                if countMalos == 10:
                    countMalos = 0
                    df.to_csv("trends.csv")
                    time.sleep(90)

                time.sleep(1)
                if countBuenos == 10:
                    countBuenos = 0
                    df.to_csv("trends.csv")
                    time.sleep(65)
                    
                if countTotal == 300:
                    countTotal = 0
                    time.sleep(240)

                if countTotal == maxCount:
                    return df

