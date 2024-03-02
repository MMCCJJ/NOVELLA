from datetime import datetime, timedelta
from pytrends.request import TrendReq
import time
import re

# hl -> hosting language
# tz -> timezone (360 = USA)
pytrends = TrendReq(hl='en-US', tz=360)

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

def restarDias(fecha_str, dias):
    """Resta el número de días dado a una fecha de tipo str"""
    
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
    fecha_resultante = fecha_obj - timedelta(days=dias)
    nueva_fecha_str = fecha_resultante.strftime('%Y-%m-%d')

    return nueva_fecha_str

def getInterestOverTime(keywords, categoria, tf):
    """Devuelve datos relacionados con el interés a lo largo del tiempo
    de la lista de keywords introducidas en una categoría y un timeframe dados"""
    
    pytrends.build_payload(keywords, cat=categoria, timeframe=tf) 
    data = pytrends.interest_over_time() 
    data = data.reset_index()
    
    return data

def getTrends(df_bestsellers):
    """Dado un dataframe de bestsellers, obtiene el interés para cada libro y autor"""
    
    interestBooks = []
    interestAuthors = []

    count = 0
    totalCount = 0
    # Recorremos todos los bestsellers
    for i, row in df_bestsellers.iterrows():

        book = row.Book
        authors = re.split(r'\s+and\s+|\s+with\s+', row.Author)

        # Creamos las listas de palabras clave
        keywordsBook = [book]
        keywordsAuthor = authors

        # Generamos los timeframes
        date = "{:04d}-{:02d}-{:02d}".format(row.Year, row.Month, row.Day)
        minusMonth = restarDias(date, 30)
        minusYear = restarDias(date, 30)
        tfM = minusMonth + " " + date
        tfY = minusYear + " " + date

        # Hacemos la request para el título
        data = getInterestOverTime(keywordsBook, CATEGORIA_LIBROS, tfM)
        interestBooks.append(sum(data[book]))

        # Hacemos la request para el autor/es
        data = getInterestOverTime(keywordsAuthor, CATEGORIA_TODAS, tfY)
        interestAuthors.append(sum([sum(data[a]) for a in authors]))


        print(totalCount)
        count += 1
        totalCount += 1

        # Congelamos para que Google no de response code 439 (demasiadas requests)
        if count == 30:
            time.sleep(2)
            count = 0

    df_bestsellers["BookInterest1M"] = interestBooks
    df_bestsellers["AuthorInterest1Y"] = interestAuthors

    return df_bestsellers


