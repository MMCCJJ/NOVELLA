import pandas as pd
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import os

def hasTwitter(soup_author):
    """Devuelve 1 si el autor del libro tiene Twitter, y 0 si no"""
    
    # Buscamos el twitter del autor
    twitter = soup_author.find('a', {'target':'_blank', 'rel':'nofollow noopener noreferrer'})
    if twitter:
        return 1
    else:
        return 0
    
def getBorn(soup_author):
    """Dada la página de un autor en goodreads extrae su lugar de nacimiento"""

    # Encontramos el elemento con el texto 'Born'
    born_element = soup_author.find("div", class_="dataTitle", text="Born")
    if born_element:
        # Obtenemos el texto correspondiente
        born_text = born_element.find_next_sibling("br").previous_sibling.strip()
        if born_text:
            return born_text
    return None

def getGenres(soup_author):
    """Dada la página de un autor en goodreads extrae una lista de sus géneros literarios"""

    try:
        # Encontramos el elemento con el texto 'Genre'
        genre_element = soup_author.find("div", class_="dataTitle", text="Genre")
        if genre_element:
            # Obtenemos el texto correspondiente
            # genre_text = genre_element.find_next_sibling("div", class_="dataItem").text.strip()

            genre_items = genre_element.find_next_sibling("div", class_="dataItem").find_all("a")
            if genre_items:
                genre_list = [item.text.strip() for item in genre_items]
                # Devolvemos la lista de géneros del autor
                return genre_list
        return None
    except Exception:
        return None
    
def getInfoAuthorGoodReads(url_libro, nombre_autor):
    """Recibe el nombre de un autor y una url de uno de sus libros, selecciona el enlace correspondiente a su perfil
    en goodreads y extrae la información"""

    print(nombre_autor)
    print(url_libro)
    
    if isinstance(url_libro, str):

        response = requests.get(url_libro)

        # Si la request tiene éxito
        if response.status_code == 200:     
            soup_libro = BeautifulSoup(response.text, "html.parser")

            # Encontrar la lista ContributorLinksList
            lista_contribuidores = soup_libro.find('div', class_='ContributorLinksList')

            # Buscamos el autor en la página del libro
            authors = lista_contribuidores.find_all('a', {'class':'ContributorLink'})
            if authors:

                if len(authors) == 1:
                    selected_author = authors[0]
                    author_url = selected_author.get('href')
                    link_name = selected_author.find('span', class_='ContributorLink__name').text

                else:
                    # Iterar sobre los enlaces y buscar el que contenga el nombre del autor
                    # Inicializar variables para el enlace seleccionado y la puntuación máxima
                    selected_link = None
                    max_score = 0

                    # Iterar sobre los enlaces y calcular la similitud del nombre del autor con el texto del enlace
                    if isinstance(nombre_autor, str):
                        for link in authors:
                            link_name = link.text.strip()
                            similarity_score = fuzz.token_sort_ratio(nombre_autor, link_name)

                            # Actualizar el enlace seleccionado si la similitud es mayor que la puntuación máxima
                            if similarity_score > max_score:
                                max_score = similarity_score
                                selected_link = link
                        if selected_link:
                            author_url = selected_link['href']
                        else:
                            author_url = None
                    else:
                        author_url = None

                response = requests.get(author_url)
                # Si la request tiene éxito
                if response.status_code == 200:
                
                    soup_author = BeautifulSoup(response.text, 'html.parser')

                    if soup_author:
                        return {
                            'HasTwitter': hasTwitter(soup_author),
                            'Born': getBorn(soup_author),
                            'Genres': getGenres(soup_author),
                            'NameSearched' : link_name
                        }
    return {
        'HasTwitter': None,
        'Born': None,
        'Genres': None,
        'NameSearched' : None
    }

def generarDfAutoresGoodReads(df_libros, ruta_carpeta):
    """Devuelve y alamacena un dataframe con información sacada de la página de goodreads de cada autor"""
    
    # Cargamos el csv con los nombres y urls de ejemplo de un libro de cada autor
    df_autores = pd.read_csv('autores_url_DEFINITIVO_DE_VERDAD.csv', index_col=0)

    # Dividimos el DataFrame en grupos de 300 filas para facilitar su procesamiento
    grupos = [df_autores.iloc[i:i+300] for i in range(0, len(df_autores), 300)]

    # Iteramos sobre los grupos y guardamos cada uno como csv en 'ruta_carpeta'
    for i, grupo in enumerate(grupos):
        df_info = grupo.apply(lambda row: getInfoAuthorGoodReads(row['URL'], row['FullName']), axis=1).apply(pd.Series)
        ruta_archivo = os.path.join(ruta_carpeta, f'autores_goodreads_{i}.csv')
        df_info.to_csv(ruta_archivo)

    # Obtenemos la lista de archivos CSV en la carpeta
    csv_files = [file for file in os.listdir(ruta_carpeta) if file.endswith('.csv')]

    # Leemos los DataFrames de cada archivo CSV y los almacenamos en una lista
    df_list = [pd.read_csv(os.path.join(ruta_carpeta, file)) for file in csv_files]

    autores_goodreads = pd.concat(df_list)
    autores_goodreads = autores_goodreads.sort_values(by="Unnamed: 0")
    autores_goodreads = autores_goodreads.reset_index(drop=True)
    autores_goodreads = autores_goodreads.drop("Unnamed: 0", axis=1)

    # Guardamos el df resultante
    autores_goodreads.to_csv('autores_goodreads.csv')

    # Lo devolvemos
    return autores_goodreads