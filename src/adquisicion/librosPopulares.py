# Importamos las librerías

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Url base de GoodReads
URL_BASE = "https://www.goodreads.com/book/popular_by_date/"

# Mes y año de inicio
MES_INI = 1
YEAR_INI = 2024

# Meses en los que retrocedemos
MESES_ATRAS = 12 * 5

def restarMes(month, year):
    """Resta un mes a la fecha dada (sin días)"""
    
    if month == 1:
        month = 12
        year -=1
    else:
        month -= 1
    return (month, year)


def getPopularBooks(ma = MESES_ATRAS, month = MES_INI, year = YEAR_INI):
    """Devuelve un dataframe con título, autor y  descripción de libros populares sacados en el mes y año
    introducidos, hasta un total de ma meses atrás"""

    DF_POPULARES = []

    # Veces que se pulsa el botón Show More
    NUM_EXPANSIONES = 13
    
    # Recorremos ma meses atrás
    for i in range(ma):

        # Configuramos el navegador
        driver = webdriver.Chrome()

        # Abrimos la página web
        fecha = str(year) + "/" + str(month)
        url = URL_BASE + fecha
        driver.get(url)

        puedeAparecerSpam = True

        # Pulsamos el botón 'Show more books' NUM_EXPANSIONES veces
        for j in range(NUM_EXPANSIONES):

            # Esperamos hasta que el botón sea visible en la página
            boton = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//button[@class='Button Button--secondary Button--small']/span[text()='Show more books']"))
            )

            """A veces aparece una pestaña de iniciar sesión que hay que cerrar"""

            if puedeAparecerSpam:

                try:
                    boton_close = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "Button--transparent"))
                    )
                    boton_close.click()
                    puedeAparecerSpam = False
                except Exception as e:
                    print(f"No ha aparecido el Spam")

            # Nos desplazamos hacia el elemento
            actions = ActionChains(driver)
            actions.move_to_element(boton).perform()

            # Hacemos click en el botón
            boton.click()

            # Esperamos a que carguen los libros
            WebDriverWait(driver, 10).until(
                EC.staleness_of(boton)
            )

        # Obtetemos el HTML de la página actualizada
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        # Contenedores de libros
        book_containers = soup.find_all("div", class_="BookListItem__body")

        titles = []
        authors = []
        descriptions = []

        # Recorremos los contenedores
        for container in book_containers:

            title_element = container.find("a", {'data-testid': 'bookTitle'})

            if title_element:

                title = title_element.text.strip().replace('[', '').replace(']', '').split('(')[0]
                titles.append(title)

                author = container.find("span", class_="ContributorLink__name").text.strip()
                authors.append(author)

                description = container.find("div", {"class": "TruncatedContent__text"}).text.strip()
                descriptions.append(description)

                data = {
                    "Title": titles,
                    "Author": authors,
                    "Description": descriptions
                }

                DF_POPULARES.append(pd.DataFrame(data))

        # Actualizamos la fecha
        month, year = restarMes(month, year)

    # Concatenamos las listas
    DF_POPULARES = pd.concat(DF_POPULARES, ignore_index=True).drop_duplicates().reset_index(drop = True)

    # Cerramos el navegador
    driver.quit()
    
    return DF_POPULARES