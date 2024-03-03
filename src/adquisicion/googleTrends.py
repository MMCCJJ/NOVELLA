import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import time
import pytrends

CATEGORIA_TODAS = 0
CATEGORIA_LIBROS = 22

def gestionarFechasParaTrends(df):
    """Filtra y prepara las fechas para que puedan ser analizadas por GoogleTrends"""

    DIAS = 20
    
    df1 = df[df["potencialBS"] == 1]

    # Convertir las columnas a tipo de dato de fecha
    df1['Date'] = pd.to_datetime(df1['Date'], errors='coerce')
    df1['DatePublished'] = pd.to_datetime(df1['DatePublished'], errors='coerce')

    # Encontrar las fechas que están fuera del rango permitido
    out_of_bounds_dates = df1[(df1['Date'].isnull()) | (df1['DatePublished'].isnull())]

    df1 = df1.drop(out_of_bounds_dates.index)

    df1['Date'] = pd.to_datetime(df1['Date'])
    df1['DatePublished'] = pd.to_datetime(df1['DatePublished'])
    df1['DaysDifference'] = (df1['Date'] - df1['DatePublished']).dt.days
    
    df2 = df[df["potencialBS"] == 0]
    df2['DatePublished'] = pd.to_datetime(df2['DatePublished'], errors='coerce')

    out_of_bounds_dates = df2[(df2['DatePublished'].isnull())]

    # Eliminar las filas con fechas fuera de rango en df2
    df2 = df2.drop(out_of_bounds_dates.index)

    # Le sumamos la mediana para calcular la columna Date
    df2['Date'] = df2['DatePublished'] + pd.Timedelta(days= DIAS)

    # Calcular la diferencia en días entre las fechas en df2
    df2['DaysDifference'] = (df2['Date'] - df2['DatePublished']).dt.days
    
    df = pd.concat([df1, df2])
    df = df[df['DaysDifference'] > 0]
    
    return df

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

            suma = sum(data[book])
            interestBooks.append(suma)
            
        except Exception as e:
            interestBooks.append(0)
            count429 += 1
        
        if count429 == 10:
            count429 = 0
            time.sleep(60)

        print(totalCount)
        totalCount += 1
        time.sleep(1)

    df["BookInterest1M"] = interestBooks

    return df

