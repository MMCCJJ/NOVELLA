import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import datetime

# Módulo para crear un dataframe con la información biográfica de los autores
def crearDfAutores(df_libros):
    """Crea y devuelve un df con los nombres de los autores y sus URLs a partir de un dataframe con libros y autores"""
    columnas = ['FullName', 'URL']
    datos_autores = []

    for index, row in df_libros.iterrows():
        if isinstance(row['Author'], str):  # Verifica si es una cadena
            autores = re.split(r'\s+and\s+|\s+with\s+', row['Author'])
            for autor in autores:
                autor = autor.strip()
                datos_autores.append({'FullName': autor, 'URL': row['url']})
    
    df_autores = pd.DataFrame(datos_autores, columns=columnas)
    df_autores = df_autores.drop_duplicates(subset=['FullName'])
    df_autores = df_autores.reset_index(drop=True)
    return df_autores

# Definimos las funciones para obtener distintos datos mediante webscraping
def getBirthday(infoCard, soup_autor):
    """Devuelve el cumpleaños del autor, y None si no encuentra la información"""

    try:
        if infoCard:
            bday = infoCard.find('span', {'class':'bday'})
            if bday:
                return bday.text
            else:
                bday = infoCard.find('td', {'class':'infobox-data'})
                if bday:
                    date = bday.find(text=True, recursive=False).strip()
    
                    parsed_date = datetime.datetime.strptime(date, "%B %d, %Y")
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
    
                    return formatted_date
        else:
            fecha_nacimiento_regex = r'born\s(.*?)\)'
            fecha_nacimiento_match = re.search(fecha_nacimiento_regex, soup_autor.text)
            if fecha_nacimiento_match:
                fecha_nacimiento = fecha_nacimiento_match.group(1)
                return fecha_nacimiento.strip()
        return None
    
    except Exception:
        return None
    
def getGender(soup_autor):
    """Devuelve el género del autor, y None si no encuentra la información"""
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
    """Devuelve el lugar de nacimiento del autor, y None si no encuentra la información"""
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
    """Devuelve el número de hijos del autor, y None si no encuentra la información"""
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
    """Devuelve el año desde el que está activo el autor, y None si no encuentra la información"""

    start_period = None

    if soup_autor:

        period_element = soup_autor.find_all('th', text=lambda x: x and "Years" in x)

        if period_element:
            period_element = period_element[0]
        else:
            if period_element:
                period = period_element.find_next('td', class_='infobox-data')
                if period:
                    start_period = period.get_text(strip=True).split('–')[0]
            else:
                period_element = soup_autor.find('th', text='Period')
                if period_element:
                    period = period_element.find_next('td', class_='infobox-data')
                    start_period = period.get_text(strip=True).split('–')[0]
                    
    return start_period

def getNationality(soup_autor):
    """Devuelve la nacionalidad de un autor"""

    # Encontramos el elemento <th> con el texto "Nationality"
    etiqueta_nationality = soup_autor.find('th', text='Nationality')

    # Si se encuentra la etiqueta, encontramos el siguiente elemento <td> y obtenemos el texto
    if etiqueta_nationality:
        nacionalidad_elemento = etiqueta_nationality.find_next_sibling('td')
        if nacionalidad_elemento:
            return nacionalidad_elemento.text.strip()
    # Si no se encuentra la etiqueta, buscamos en el texto
    else:
        # Expresión regular para extraer la nacionalidad
        nacionalidad_regex = r'is\s(?:an?\s)?([A-Za-z]+)\s(?:novelist|writer)'
        nacionalidad_match = re.search(nacionalidad_regex, soup_autor.text)
        if nacionalidad_match:
            return nacionalidad_match.group(1)
    return None

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

        # Verificamos si la página contiene la frase "may refer to:"
        may_refer_to = soup_autor.find("div", class_="mw-content-ltr mw-parser-output")
        if may_refer_to and "may refer to:" in may_refer_to.text:
            # Encontramos enlaces que contienen las palabras "novelist" o "writer"
            novelist_link = soup_autor.find("a", href=lambda href: href and ("novelist" in href.lower() or "writer" in href.lower()))
            if novelist_link:
                novelist_url = novelist_link["href"]
                # Construimos la URL completa si es relativa
                if novelist_url.startswith("/"):
                    novelist_url = "https://en.wikipedia.org" + novelist_url
                # Hacemos click en el enlace
                response = requests.get(novelist_url)
                if response.status_code == 200:
                    soup_autor = BeautifulSoup(response.text, 'html.parser')

        # Buscamos el panel de información del autor
        infoCard = soup_autor.find('table', {'class': 'infobox vcard'})
        if not infoCard:
            infoCard = soup_autor.find('table', {'class': 'infobox biography vcard'})
    else:
        # Probamos solo con el nombre
        url = URL_BASE + nombre_autor_formateado
        response = requests.get(url)
        
        if response.status_code == 200:
        
            soup_autor = BeautifulSoup(response.text, 'html.parser')

            # Buscamos el panel de información del autor
            infoCard = soup_autor.find('table', {'class': 'infobox vcard'})
            if not infoCard:
                infoCard = soup_autor.find('table', {'class': 'infobox biography vcard'})
        else:
            print("No se ha encontrado la página de Wikipedia")
            soup_autor, infoCard = None, None
        
    print("----------------------------------------",nombre_autor)
    
    if soup_autor:
        return {
            'Birthday': getBirthday(infoCard, soup_autor),
            'Gender': getGender(soup_autor),
            'Birthplace': getBirthplace(infoCard),
            'NumChild':getNumChild(soup_autor),
            'StartYear': getStartYear(soup_autor),
            'Nationality': getNationality(soup_autor)
        }
    else:
        return {
            'Birthday': None,
            'Gender': None,
            'Birthplace': None,
            'NumChild':None,
            'StartYear': None,
            'Nationality': None
        }

def generarDfAutores(df_libros):
    """Genera y devuelve un df con la información de los autores recopilada de Wikipedia a partir de los autores del df de libros de entrada"""
    df_autores = crearDfAutores(df_libros)
    df_autores.to_csv('autores_url.csv')

    # Creamos un df con la info recopilada de GoodReads
    df_info = df_autores['FullName'].apply(getInfoAutor).apply(pd.Series)

    # Combinamos los dfs
    df_autores = pd.concat([df_autores, df_info], axis=1)

    # Guardamos el csv resultante
    df_autores.to_csv('autores.csv')

    return df_autores