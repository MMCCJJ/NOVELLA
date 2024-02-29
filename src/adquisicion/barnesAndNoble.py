from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

def getPrice(nombre_libro):
    """Devuelve el precio de un libro en Barnes & Noble y su formato (hardcover, paperback...)"""
    
    nombre_libro_formateado = re.sub(r"[!,*)@#%(&$_?.^'-]", '', nombre_libro).lower().replace(' ', '+')

    # Obtenemos la url
    base_url: str='https://www.barnesandnoble.com/s/'
    url = base_url + nombre_libro_formateado
    print(url)
    
    driver = webdriver.Chrome()
    
    driver.get(url)

    # Obtenemos el elemento con el precio si aparece
    try:
        price_element = driver.find_element(By.CLASS_NAME, 'product-shelf-pricing').text.strip()
        price_elements = price_element.split()
    except NoSuchElementException:
        print("No se encontró el precio")
        # Si no se encuentra devolvemos None
        return {'Price': None, 'PriceFormat': None}
    
    # Obtenemos el formato
    price_format = price_elements[0]

    # Obtenemos el precio si aparece (probamos con el segundo y tercer elemento)
    try:
        price = float(price_elements[1].replace('$', ''))
    except ValueError:
        try:
            price = float(price_elements[2].replace('$', ''))
        except IndexError:
            price = None
        
    return {'Price': price, 'PriceFormat': price_format}