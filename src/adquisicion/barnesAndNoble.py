from selenium import webdriver
from selenium.webdriver.common.by import By
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
    
    price_element = driver.find_element(By.CLASS_NAME, 'product-shelf-pricing').text.strip()
    price_elements = price_element.split()
    
    price_format = price_elements[0]
    price = float(price_elements[1].replace('$', ''))
        
    return(price, price_format)