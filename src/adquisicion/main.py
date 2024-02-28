import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

import librosNYT
import goodreads
import barnesAndNoble
import googleTrends

def main():

    # Obtenemos un dataframe con los bestsellers del NYT
    df_nyt = librosNYT.getBooksNYT()
    df_nyt.to_csv('librosNYT.csv')

    # Creamos un dataframe con la información adicional de cada libro
    df_info = df_nyt['Title'].apply(getInfoLibro).apply(pd.Series)

    # Combinamos los dfs
    df_bestsellers = pd.concat([df_nyt, df_info], axis=1)

    # Obtenemos el número de premios de cada libro
    df_premios = df_bestsellers.apply(lambda row: goodreads.getNumAwards(row['url'], row['Date']), axis=1)

    # Combinamos los dfs
    df_bestsellers = pd.concat([df_bestsellers, df_premios], axis=1)
    df_bestsellers.to_csv('bestsellers.csv')

    # Obtenemos un dataframe con los precios
    df_precios = df_bestsellers['Title'].apply(barnesAndNoble.getPrice).apply(pd.Series)

    # Combinamos los dfs
    df_bestsellers = pd.concat([df_bestsellers, df_precios], axis=1)

    # Obtenemos la información de googleTrends
    df_bestsellers = googleTrends.getTrends(df_bestsellers)

def getInfoLibro(nombre_libro):
    """Devuelve un diccionario con información de un libro dado"""
    
    nombre_libro_formateado = re.sub(r"[!,*)@#%(&$_?.^'-]", '', nombre_libro).lower().replace(' ', '+')
    
    # Buscamos el nombre del libro en goodreads
    url = "https://www.goodreads.com/search?q=" + nombre_libro_formateado
    
    response = requests.get(url)
    
    # Si la request tiene éxito
    if response.status_code == 200:
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seleccionamos la tabla del html con los resultados de la búsqueda
        table = soup.select('.tableList')

        if table:
        
            # Seleccionamos el primer resultado
            first_row = table[0].find('tr')
            
            # Obtenemos el valor de 'href' que corresponde a la url de la página del libro
            libro = first_row.find('a', class_='bookTitle')
            href_libro = libro.get('href')
            
            # Accedemos a la página del libro en goodreads
            url_libro = "https://www.goodreads.com" + href_libro
            response = requests.get(url_libro)
            print(url_libro)
            
            # Si la request tiene éxito
            if response.status_code == 200:
                
                soup_libro = BeautifulSoup(response.text, "html.parser")
                
                # Obtenemos la presencia de color en la portada del libro
                img_tag = soup_libro.find('img', {'class': 'ResponsiveImage'})
                
                if img_tag:
                    img_src = img_tag.get('src')
                porcentajesColores = goodreads.getColorPercentage(img_src)

                
                return {
                    'Rating': goodreads.getRating(soup_libro),
                    'NumPages': goodreads.getNumPages(soup_libro),
                    'GenresList': goodreads.getGenresList(soup_libro),
                    'Type': goodreads.getType(soup_libro),
                    'DatePublished': goodreads.getDatePublished(soup_libro),
                    'SagaName': goodreads.getSagaName(soup_libro),
                    'SagaNumber': goodreads.getSagaNumber(soup_libro),
                    'RedPerc': porcentajesColores["porcentaje_rojo"],
                    'BluePerc': porcentajesColores["porcentaje_azul"],
                    'GreenPerc': porcentajesColores["porcentaje_verde"],
                    'url': url_libro
                }
        
if __name__ == "__main__":
    main()