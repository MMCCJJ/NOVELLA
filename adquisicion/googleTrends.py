import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import time
import pytrends

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


def getTrends(df):
    """Dado un dataframe de bestsellers, obtiene el interés para cada libro en el periodo
    de un mes"""
    
    interestBooks = []

    # hl -> hosting language
    # tz -> timezone (360 = USA)
    pytrends = TrendReq(hl='en-US', tz=360)

    # Nos aseguramos de que la columna Date sea una fecha
    df['Date'] = pd.to_datetime(df['Date'])

    count429 = 0
    totalCount = 0
    # Recorremos todos los bestsellers
    for i, row in df.iterrows():

        book = row.Title

        # Creamos las listas de palabras clave
        keywordsBook = [book]

        # Generamos los timeframes
        date = row.Date
        minusMonth = date - timedelta(days=30)
        tfM = minusMonth.strftime("%Y-%m-%d") + " " + date.strftime("%Y-%m-%d")

        # Hacemos la request para el título
        data = getInterestOverTime(keywordsBook, CATEGORIA_LIBROS, tfM)
        try:

            # Si tiene éxito se suman las puntuaciones y se añade a la lista
            suma = sum(data[book])
            interestBooks.append(suma)
            
        except Exception as e:

            # Si hay un error se añade un 0 a la lista
            interestBooks.append(0)
            count429 += 1
        
        # Pausa tras varios errores 429 para suavizar los bloqueos
        if count429 == 10:
            count429 = 0
            time.sleep(60)

        print(totalCount)
        totalCount += 1
        time.sleep(1)

    # Creamos la columna con los datos obtenidos
    df["BookInterest1M"] = interestBooks

    return df

