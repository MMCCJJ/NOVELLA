""" OTRA OPCIÓN A PROBAR """


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import time

df = pd.read_csv("LIBROS.csv")
df['Date'] = pd.to_datetime(df['Date'])

df2 = df[df['DatePublished'] > '2018-01-01']


# Ordenar el DataFrame por fecha
df_sorted = df2.sort_values(by='Date')

# Inicializar la lista de diccionarios
lista_diccionarios = []

for i in range(0, len(df_sorted), 5):
    # Obtener los títulos en el grupo actual
    titulos_grupo = df_sorted.iloc[i:i+5]['Title'].tolist()
    # Obtener la fecha del último título en el grupo actual
    fecha_ultimo_titulo = df_sorted.iloc[i]['Date']  # El último título del grupo es el índice i+3
    # Crear el diccionario
    diccionario = {'titulos': titulos_grupo, 'fecha_ultimo_titulo': fecha_ultimo_titulo}
    # Agregar el diccionario a la lista
    lista_diccionarios.append(diccionario)


# hl -> hosting language
# tz -> timezone (360 = USA)
pytrends = TrendReq(hl='en-US', tz=360)
# Función para obtener el interés a lo largo del tiempo para una lista de palabras clave
def obtener_interes_a_lo_largo_del_tiempo(palabras_clave, tf):
 
    
    pytrends.build_payload(palabras_clave, timeframe=tf, cat=22)
    interes_a_lo_largo_del_tiempo = pytrends.interest_over_time()
    return interes_a_lo_largo_del_tiempo


i = 0
for diccionario in lista_diccionarios:
    titulos_grupo = diccionario['titulos']
    fecha_ultimo_titulo = diccionario['fecha_ultimo_titulo']
    
    date = fecha_ultimo_titulo
    minusMonth = date - timedelta(days=30)
    tfM = minusMonth.strftime("%Y-%m-%d") + " " + date.strftime("%Y-%m-%d")
        
    
    try:
        # Obtener el interés a lo largo del tiempo para las palabras clave
        interes_data = obtener_interes_a_lo_largo_del_tiempo(titulos_grupo, tfM)
        
        # Añadir los datos de interés a lo largo del tiempo al DataFrame original
        try:
            for titulo in titulos_grupo:
                df.loc[df['Title'] == titulo, 'InterestOverTime'] = interes_data[titulo].sum()
        except Exception as e:
            print(f"Error: {e}. Agregando 0 a la columna InterestOverTime para {titulo}")
            
    except Exception as e:
        print(f"Error: {e}. Agregando 0 a la columna InterestOverTime para el grupo de títulos {titulos_grupo}")
        # Añadir 0 a la columna InterestOverTime para todos los títulos del grupo
        for titulo in titulos_grupo:
            df.loc[df['Title'] == titulo, 'InterestOverTime'] = 0
    
    i += 1
    
    # Esperar 30 segundos antes de la siguiente solicitud a Google Trends
    print(i)
    time.sleep(2)


