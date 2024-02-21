from datetime import datetime, timedelta
from pytrends.request import TrendReq
import time
import re

# hl -> hosting language
# tz -> timezone (360 = USA)
pytrends = TrendReq(hl='en-US', tz=360)

CATEGORIA_TODAS = 0
CATEGORIA_LIBROS = 22

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