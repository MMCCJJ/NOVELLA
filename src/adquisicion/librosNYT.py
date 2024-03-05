import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- CONSTANTES ---

# URL base de la lista NYT
URL_BASE = "https://www.nytimes.com/books/best-sellers/"

# Fecha inicial
YEAR_INI = 2024
MONTH_INI = 2
DAY_INI = 4

# Semanas a retroceder por defecto
WEEKS_BACK = 52 * 5

"""
    La lista NYT tiene distintas categorías para los libros bestsellers.
    Aquí se encuentran sus urls base clasificados en un diccionario.
"""
CATEGORIES_WITH_URLS = {
    "FICTION": {
        "Combined Print & E-Book Fiction": "/combined-print-and-e-book-fiction/",
        "Hardcover Fiction": "/hardcover-fiction/",
        "Paperback Trade Fiction": "/trade-fiction-paperback/"
    }
}

"""

Resto de categorías:

    "NONFICTION": {
        "Combined Print & E-Book Nonfiction": "/combined-print-and-e-book-nonfiction/",
        "Hardcover Nonfiction": "/hardcover-nonfiction/",
        "Paperback Nonfiction": "/paperback-nonfiction/",
        "Advice, How-To & Miscellaneous": "/advice-how-to-and-miscellaneous/"
    },
    "CHILDREN": {
        "Children’s Middle Grade Hardcover": "/childrens-middle-grade-hardcover/",
        "Children’s Picture Books": "/picture-books/",
        "Children’s Series": "/series-books/",
        "Young Adult Hardcover": "/young-adult-hardcover/"
    }

"""

# ---  FUNCIONES ---
def minusWeek(day, month, year):
    """ Devuelve la fecha introducida menos una semana"""

    date = datetime(year, month, day)
    new_date = date - timedelta(weeks=1)
    return new_date.day, new_date.month, new_date.year

def getBooksNYT(day = DAY_INI, month = MONTH_INI, year = YEAR_INI, wb = WEEKS_BACK):
    """Accede a la lista NYT a partir de la fecha dada hasta wb semanas atrás y devuelve 
    un dataframe con información acerca de estos libros"""

    # dataframe en el que se almacenarán los bestellers
    DF_BESTSELLERS = pd.DataFrame()

    # Retrocedemos tantas semanas como indiquemos (por defecto 52)
    for i in range(wb):

        fechaURL = str(year) + "/" + str(month).zfill(2) + "/" + str(day).zfill(2)

        # Recorremos las categorías y subcategorías de bestsellers
        for main_category, subcategories in CATEGORIES_WITH_URLS.items():
            for subcategory, subcategory_url in subcategories.items():
                
                # Generamos la url y hacemos la request
                url = URL_BASE + fechaURL + subcategory_url
                response = requests.get(url)

                # Si la request tiene éxito
                if response.status_code == 200:

                    soup = BeautifulSoup(response.text, 'html.parser')
                    list_items = soup.find_all('li', class_='css-13y32ub')

                    books = []

                    # Recopilamos la información de los libros
                    for item in soup.find_all('li', class_='css-13y32ub'):

                        title = item.find('h3').text.strip()
                        author = item.find('p', class_='css-hjukut').text.strip()[3:] 
                        publisher = item.find('p', class_='css-heg334').text.strip()
                        description = item.find('p', itemprop='description').text.strip()
                        weeks_on_list = item.find('p', class_='css-1o26r9v').text.strip().split()[0].replace("New", "1")
                        date = datetime(year, month, day)

                        books.append({'Title': title, 'Author': author, 'Publisher': publisher, 'Description': description, 'Weeks on List': weeks_on_list, 'Date': date, 'Main Category': main_category, 'Subcategory': subcategory})
                    
                    # Actualizamos el dataframe
                    DF_BESTSELLERS = pd.concat([DF_BESTSELLERS, pd.DataFrame(books)])

        # Restamos una semana
        day, month, year = minusWeek(day, month, year)

    return DF_BESTSELLERS
    
