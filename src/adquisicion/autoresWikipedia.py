import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

# Módulo para crear un dataframe con la información biográfica de los autores
def crearDfAutores(df_libros):
    """ Crea y devuelve un df con los nombres de los autores a partir de un dataframe con libros y autores"""
    columnas = ['FullName']
    df_autores = pd.DataFrame(columns = columnas)

    for a in df_libros['Author'].unique():
        nombres = [name.strip() for name in re.split(r'\s+and\s+|\s+with\s+', a)]
        for n in nombres:
            df_autores.loc[len(df_autores), 'FullName'] = n.capitalize()
    
    return df_autores

# Definimos las funciones para obtener distintos datos mediante webscraping
def getBirthday(soup_autor):
    """ Devuelve el cumpleaños del autor, y None si no encuentra la información """
    if soup_autor:
        bday = soup_autor.find('span', {'class':'bday'})
        if bday:
            return bday.text
        else:
            bday = soup_autor.find('td', {'class':'infobox-data'})
            date = bday.find(text=True, recursive=False).strip()
            
            parsed_date = datetime.strptime(date, "%B %d, %Y")
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            
            return formatted_date
    else:
        return None
    
def getGender(soup_autor):
    """ Devuelve el género del autor, y None si no encuentra la información """
    if soup_autor:
        info = soup_autor.find('div', {'class': 'mw-content-ltr mw-parser-output'})
        if info:
            paragraphs = info.find_all('p', recursive=False)

            # Buscamos el primer parrafo que no esta vacio
            for paragraph in paragraphs:
                if paragraph.get_text(strip=True):
                    plain_text = paragraph.get_text().lower()

                    pronoun_counts = {'he': 0, 'his': 0, 'she': 0, 'her': 0}

                    # Contamos los pronombres
                    for p in pronoun_counts.keys():
                        pronoun_counts[p] += plain_text.split().count(p)

                    # Determinamos el género en base a los pronombres extraidos
                    if pronoun_counts['he'] + pronoun_counts['his'] > pronoun_counts['she'] + pronoun_counts['her']:
                        gender = 'M'
                    elif pronoun_counts['she'] + pronoun_counts['her'] > pronoun_counts['he'] + pronoun_counts['his']:
                        gender = 'F'
                    else:
                        gender = None

                    return gender

        else:
            return None

        return gender
    else:
        return None

def getBirthplace(soup_autor):
    """ Devuelve el lugar de nacimiento del autor, y None si no encuentra la información """
    if not soup_autor:
        return None
    
    born = soup_autor.find('th', text='Born')
    if not born:
        return None

    info = born.find_next('td', class_='infobox-data')
    if not info:
        return None
    
    text_contents = info.find_all(text=True)
    if not text_contents:
        return None
    
    text_content = text_contents[-1]
    if '(' in str(text_content):
        return None
    
    return text_content.strip(',')

def getNumChild(soup_autor):
    """ Devuelve el número de hijos del autor, y None si no encuentra la información """
    if soup_autor:
        # Find the element with the class 'infobox-data' within the 'td' tag under 'th' with text 'Children'
        children_element = soup_autor.find('th', text='Children')
        if children_element:
            children = children_element.find_next('td', class_='infobox-data')

            # Extract the text content (which should be '3')
            num_child = children.get_text(strip=True)
            if not num_child.isdigit():
                num_child = None
        else:
            return None

        return num_child
    else:
        return None
    
def getStartYear(soup_autor):
    """ Devuelve el año desde el que está activo el autor, y None si no encuentra la información """
    if soup_autor:
        
        period_element = soup_autor.find_all('th', text=lambda x: x and "Years" in x)
        
        if period_element:
            period_element = period_element[0]
        else:
            return None

        if period_element:
            period = period_element.find_next('td', class_='infobox-data')
            start_period = period.get_text(strip=True).split('–')[0]
        else:
            period_element = soup_autor.find('th', text='Period')
            print(3, period_element)
            if period_element:
                period = period_element.find_next('td', class_='infobox-data')
                start_period = period.get_text(strip=True).split('–')[0]

            else:
                return None

        return start_period
    else:
        return None
    
def hasTwitter(soup_libro):
    """Devuelve 1 si el autor del libro tiene Twitter, y 0 si no"""

    # Buscamos el autor en la página del libro
    author = soup_libro.find('a', {'class':'ContributorLink'})
    author_url = author.get('href')
    response = requests.get(author_url)
    
    # Si la request tiene éxito
    if response.status_code == 200:
        
        soup_autor = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos el twitter del autor
        twitter = soup_autor.find('a', {'target':'_blank', 'rel':'nofollow noopener noreferrer'})
        if twitter:
            return 1
        else:
            return 0

       
def getInfoAutor(nombre_autor):
    """Función que devuelve un diccionario con info de un autor en base a los datos de la wikipedia"""

    URL_BASE = "https://en.wikipedia.org/wiki/"
    AUTHOR_SUFFIX = "_(author)"
    
    nombre_autor_formateado = nombre_autor.replace(" ", "_")

    # Generamos el url de Wikipedia
    # Puede que no encuentre la página porque haya varias personas con el mismo nombre
    # Probamos primero si hay que desambiguar
    
    url = URL_BASE + nombre_autor_formateado + AUTHOR_SUFFIX
    
    response = requests.get(url)
    
    # Si la request tiene éxito
    if response.status_code == 200:
        
        soup_autor = BeautifulSoup(response.text, 'html.parser')
        infoCard = soup_autor.find('table', {'class': 'infobox vcard'})
        if not infoCard:
            infoCard = soup_autor.find('table', {'class': 'infobox biography vcard'})
    else:
        # Probamos solo con el nombre
        url = URL_BASE + nombre_autor_formateado
        response = requests.get(url)
        
        if response.status_code == 200:
        
            soup_autor = BeautifulSoup(response.text, 'html.parser')
            infoCard = soup_autor.find('table', {'class': 'infobox vcard'})
            if not infoCard:
                infoCard = soup_autor.find('table', {'class': 'infobox biography vcard'})
        else:
            soup_autor, infoCard = None, None
        
    print("----------------------------------------",nombre_autor)
    
    
    return {
        'Birthday': getBirthday(infoCard),
        'Gender': getGender(soup_autor),
        'Birthplace': getBirthplace(infoCard),
        'NumBestSell': getNumBestSell(nombre_autor),
        'NumChild':getNumChild(soup_autor),
        'startYear': getStartYear(soup_autor),
        'HasTwitter': getHasTwitter(soup_autor)
    }

def generarDfAutores(df_libros):
    """ Genera y devuelve un df con la información de los autores recopilada de Wikipedia a partir de los autores del df de libros de entrada"""
    df_autores = crearDfAutores(df_libros)

    # Creamos un df con la info recopilada de GoodReads
    df_info = df_autores['FullName'].apply(getInfoAutor).apply(pd.Series)

    # Combinamos los dfs
    df_autores = pd.concat([df_autores, df_info], axis=1)

    # Convertimos los nombres de los autores en el índice del df
    df_autores = df_autores.set_index('FullName')

    return df_autores