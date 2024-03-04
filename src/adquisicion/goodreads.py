import requests
from PIL import Image
from io import BytesIO
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def getRating(soup_libro):
    """Devuelve el rating actual del libro""" 

    rating_div = soup_libro.find('div', class_='RatingStatistics__rating')
    return float(rating_div.text)

def getNumPages(soup_libro):
    """Devuelve el número de páginas del libro"""

    pages_paragraph = soup_libro.find('p', {'data-testid': 'pagesFormat'})
    pages_text = pages_paragraph.text.split()[0]
    return int(pages_text)

def getGenresList(soup_libro):
    """Devuelve la lista de géneros de un libro"""
    
    genres_ul = soup_libro.find('ul', {'class': 'CollapsableList', 'aria-label': 'Top genres for this book'})
    genre_links = genres_ul.find_all('span', class_='Button__labelItem')
    
    # El último género es ...more
    return list(set([link.text for link in genre_links[:-1]]))
    
def getNumReviews(soup_libro):
    """Devuelve el número de reviews del libro"""
   
    reviews_span = soup_libro.find('span', {'data-testid': 'reviewsCount'})
    reviews_text = reviews_span.text.split()[0].replace(',', '')
    return int(reviews_text)

def getType(soup_libro):
    """Devuelve el formato del libro"""

    format_paragraph = soup_libro.find('p', {'data-testid': 'pagesFormat'})

    if format_paragraph:
        format_text = format_paragraph.text.lower()
        split_result = format_text.split(', ')

        if len(split_result) > 1:
            book_type = split_result[1]
            return book_type
        else:
            return None 
    else:
        return None  

def getDatePublished(soup_libro):
    """Devuelve la fecha de publicación del libro"""
 
    publication_info_paragraph = soup_libro.find('p', {'data-testid': 'publicationInfo'})

    if publication_info_paragraph:
        publication_info_text = publication_info_paragraph.text.lower()
        split_result = publication_info_text.split('first published ')

        if len(split_result) > 1:
            publication_date = split_result[1]
            return publication_date
        else:
            return None
    else:
        return None
    
def getSagaName(soup_libro):
    """Devuelve el nombre de la saga del libro. Si no pertenece a una saga devuelve NaN"""
    
    h3_element = soup_libro.find('h3', {'class':'Text Text__title3 Text__italic Text__regular Text__subdued'})

    if h3_element:
        saga_info = h3_element.text.strip().split(' ')
        saga_name = ' '.join(saga_info[:-1])
        
        return saga_name
    else:
        return "NaN"
    
def getSagaNumber(soup_libro):
    """Devuelve el número del libro en la saga a la que pertenece. Si no pertenece a una saga devuelve NaN"""
    
    h3_element = soup_libro.find('h3', {'class':'Text Text__title3 Text__italic Text__regular Text__subdued'})

    if h3_element:
        saga_info = h3_element.text.strip().split(' ')
        saga_number = saga_info[-1].replace('#', '')
        
        return saga_number
    else:
        return "NaN"
    
def getNumAwards(url_libro, date):
    """Devuelve un diccionario con el número de premios literarios que ha ganado un libro antes de ser bestseller"""
    
    try:
        # Inicializar el navegador (tener el driver correspondiente, como ChromeDriver)
        driver = webdriver.Chrome()

        # Abrir la página web
        driver.get(url_libro)

        # Si aparece una pestaña de "Discover and Read More", la cerramos
        puedeAparecerSpam = True
        if puedeAparecerSpam:

            try:
                boton_close = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "Button--transparent"))
                )
                boton_close.click()
                puedeAparecerSpam = False
            except Exception as e:
                print("No ha aparecido la pestaña 'Discover'")

        # Encontramos el botón desplegable que contiene los premios y hacemos click en él
        button = driver.find_element(By.XPATH, "//button[@aria-label='Book details and editions']")
        
        # Nos desplazamos hacia el elemento
        actions = ActionChains(driver)
        actions.move_to_element(button).perform()
            
        button.click()

        # Hacemos click en el botón "Show more" si aparece
        try:
            button = driver.find_element(By.XPATH, "//button[@aria-label='Show more Literary awards']")
            button.click()
        except NoSuchElementException:
            print("El botón 'Show more Literary awards' no fue encontrado")

        # Obtenemos todos los premios
        awards = driver.find_elements(By.XPATH, "//span[@data-testid='award']")

        # Inicializamos el contador
        num_premios = 0

        # Para cada premio recibido
        for award_element in awards:

            # Obtenemos el texto
            award_text = award_element.text
          
            # Extraemos el año del premio
            award_year = int(award_text.split("(")[-1].split(")")[0])
        
            # Si el premio es anterior a la fecha en la que el libro fue bestseller, incrementamos el contador
            year = date.year
            if award_year < year:
                num_premios += 1

        # Cerrar el navegador
        driver.quit()

        return {'NumAwards': num_premios}
    except Exception as e:
        return {'NumAwards': 0}


def getColorPercentage(url):
    """Analiza la presencia de color en la portada de un libro"""
    
    # Descargamos la imagen desde la URL
    response = requests.get(url)
    
    porcentaje_rojo = None
    porcentaje_verde = None
    porcentaje_azul = None
        
    if response.status_code == 200:
        
        img = Image.open(BytesIO(response.content))

        # Obtenemos los píxeles de la imagen
        pixels = img.getdata()

        # Inicializamos contadores para cada color
        conteo_rojo = conteo_verde = conteo_azul = 0

        # Contamos la cantidad de píxeles de cada color
        for pixel in pixels:
            r, g, b = pixel
            conteo_rojo += r
            conteo_verde += g
            conteo_azul += b

        # Calculamos el porcentaje de cada color
        total_pixeles = len(pixels)
        porcentaje_rojo = round((conteo_rojo / (total_pixeles * 255)), 2)
        porcentaje_verde = round((conteo_verde / (total_pixeles * 255)), 2)
        porcentaje_azul = round((conteo_azul / (total_pixeles * 255)), 2)


    # Devolver los resultados
    return {
        "porcentaje_rojo": porcentaje_rojo,
        "porcentaje_verde": porcentaje_verde,
        "porcentaje_azul": porcentaje_azul
    }

def getInfoLibro(nombre_libro):
    """Devuelve un diccionario con información de un libro dado"""
    
    nombre_libro_formateado = re.sub(r"[!,*)@#%(&$_?.^'-]", '', nombre_libro).lower().replace(' ', '+')
    
    # Buscamos el nombre del libro en goodreads
    url = "https://www.goodreads.com/search?q=" + nombre_libro_formateado
    
    try:
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
                print(url_libro)
                response = requests.get(url_libro)

                # Si la request tiene éxito
                if response.status_code == 200:

                    soup_libro = BeautifulSoup(response.text, "html.parser")

                    try:
                        
                        # Obtenemos la presencia de color en la portada del libro
                        img_tag = soup_libro.find('img', {'class': 'ResponsiveImage'})

                        if img_tag:
                            img_src = img_tag.get('src')
                            
                        porcentajesColores = getColorPercentage(img_src)
                        
                        return {
                            'Rating': getRating(soup_libro),
                            'NumPages': getNumPages(soup_libro),
                            'GenresList': getGenresList(soup_libro),
                            'Type': getType(soup_libro),
                            'DatePublished': getDatePublished(soup_libro),
                            'SagaName': getSagaName(soup_libro),
                            'SagaNumber': getSagaNumber(soup_libro),
                            'RedPerc': porcentajesColores["porcentaje_rojo"],
                            'BluePerc': porcentajesColores["porcentaje_azul"],
                            'GreenPerc': porcentajesColores["porcentaje_verde"],
                            'url': url_libro
                        }
                    except Exception as e:
                        print(f"Error: {e}")

                        return {
                            'Rating': None,
                            'NumPages': None,
                            'GenresList': None,
                            'Type': None,
                            'DatePublished': None,
                            'SagaName': None,
                            'SagaNumber': None,
                            'RedPerc': None,
                            'BluePerc': None,
                            'GreenPerc': None,
                            'url': None
                        }
    except Exception as e:
        print(f"Error de conexión: {e}")

    return {
        'Rating': None,
        'NumPages': None,
        'GenresList': None,
        'Type': None,
        'DatePublished': None,
        'SagaName': None,
        'SagaNumber': None,
        'RedPerc': None,
        'BluePerc': None,
        'GreenPerc': None,
        'url': None
    }
