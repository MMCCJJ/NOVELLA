import pandas as pd
import re
import country_converter as coco
import pyarrow.parquet as pq

IMPUREZAS_AUTORES = [
            ", edited by ",
            ". Illustrated by ",
            "tten and illustrated by ",
            'ted by',
            'h an introduction by',
            'h related materials by ',
            'the office of the special counsel',
            'et al. Illustrated by',
            '. Edited by',
            ', with recipes by',
            'as told to'
            ]

# Cargamos un csv con nacionalidades y países
DF_NACIONALIDADES = pd.read_csv('demonyms.csv', names=['Nationality', 'Country'])

def corregirAutores(df):
    """Corrige los nombres de los autores, eliminando espacios en blanco sobrantes y otras impurezas encontradas"""

    df["FullName"] = df["FullName"].apply(str.strip)

    def quitarImpurezas(x):
        for i in IMPUREZAS_AUTORES: 
            x = x.split(i, 1)[0]
        return x
        
    df["FullName"] = df["FullName"].apply(quitarImpurezas)
    
    return df

def eliminarErroresWiki(df):
    """Elimina errores de la información extraída de Wikipedia"""
    
    columnas_a_eliminar = ["Birthday", "Gender", "Birthplace", "NumChild", "StartYear", "HasTwitter"]
    df = df.drop(columnas_a_eliminar, axis=1)

    # Renombrar columnas
    nuevos_nombres = {'Birthday.1': 'Birthday', 'Gender.1': 'Gender', 'Birthplace.1': 'Birthplace', 'NumChild.1': 'NumChild', 'StartYear.1': 'StartYear'}
    df.rename(columns=nuevos_nombres, inplace=True)
    
    return df

def eliminarFilasNulas(df):
    """Elimina las filas que tengan todas las columnas con valores nulos"""

    # Seleccionamos las filas donde todas las columnas especificadas están a NaN
    null_rows_index = df[df[["Birthday", "Gender", "Birthplace", "NumChild", "StartYear", "Nationality", "HasTwitter", "Born", "Genres"]].isnull().all(axis=1)].index

    # Eliminamos las filas seleccionadas
    df = df.drop(null_rows_index)

    return df

def filtrarFilas(df):
    """Si el nombre del autor buscado en goodreads no es el que debería de ser pone
    las columnas con la información de goodreads a None ya que esta información no
    es válida"""

    columnas_modificar = ["HasTwitter", "Born",	"Genres"]

    # Aplicamos el filtro
    filtro = df["FullName"] != df["NameSearched"]

    df.loc[filtro, columnas_modificar] = None

    return df

def hasWikipedia(row):
    """Crea la variable hasWikipedia"""

    if row[["Birthday", "Gender", "Birthplace", "NumChild", "StartYear", "Nationality"]].isnull().all():
        return 0
    else:
        return 1
    
def columnaAInt(df, column):
    """Transforma los valores de una columna a enteros"""

    df[column] = df[column].astype('Int64', errors='ignore')
    return df

def extraerAnio(fecha):
    """Extrae el año de nacimiento de un autor a partir de su fecha de nacimiento"""

    # Busca un patrón de 4 dígitos para el año
    anio = re.findall(r'\b\d{4}\b', str(fecha))
    # Retorna el primer año encontrado, o None si no se encuentra ninguno
    return int(anio[0]) if anio else pd.NA

def obtenerPaisDeNacionalidad(nacionalidad):
    """Función para obtener el país correspondiente a una nacionalidad"""
    
    if nacionalidad in DF_NACIONALIDADES['Nationality'].values:
        return DF_NACIONALIDADES[DF_NACIONALIDADES['Nationality'] == nacionalidad]['Country'].iloc[0]
    else:
        return None
    
def extraerPais(row):
    """Extrae el país de un autor a partir de su lugar de nacimiento o nacionalidad"""
    
    # Expresión regular para buscar el país
    regex_pais = r',?\s*(U\.?S\.?|U\.S\.A\.?|[a-zA-Z\s]+)$'
    
    # Busca en la columna 'Birthplace'
    if pd.notna(row['Birthplace']):
        match = re.search(regex_pais, row['Birthplace'])
        if match:
            return match.group(1).strip()
    
    # Busca en la columna 'Born'
    if pd.notna(row['Born']):
        match = re.search(regex_pais, row['Born'])
        if match:
            return match.group(1).strip()
        
    if pd.notna(row['Nationality']):
        return obtenerPaisDeNacionalidad(row['Nationality'])
    
    return pd.NA  # Si no se encuentra el país, devuelve pd.NA
    
def limpiaAutores():
    """Limpia la información de los autores extraída de Wikipedia y goodreads"""
    # Cargamos los autores con la información de Wikipedia
    autores_wiki = pd.read_csv('autores.csv', index_col=0)

    autores_wiki = corregirAutores(autores_wiki)
    autores_wiki = eliminarErroresWiki(autores_wiki)

    # Cargamos los autores con la información de goodreads
    autores_goodreads = pd.read_csv('autores_goodreads.csv', index_col=0)

    autores_goodreads = corregirAutores(autores_goodreads)

    # Combinamos los dataframes
    autores_merge = pd.merge(autores_wiki, autores_goodreads, on='FullName', how='left')
    
    # Ordenamos alfabéticamente por nombre
    autores = autores_merge.sort_values(by='FullName')

    autores = eliminarFilasNulas(autores)

    # Generamos la nueva columna HasWikipedia
    autores['HasWikipedia'] = autores.apply(lambda row: hasWikipedia(row), axis=1)

    autores = filtrarFilas(autores)

    # Eliminamos columnas que ya no tienen utilidad
    autores = autores.drop(['NameSearched', 'URL'], axis=1)

    autores = columnaAInt(autores, "NumChild")
    autores = columnaAInt(autores, "StartYear")
    autores = columnaAInt(autores, "HasTwitter")

    # Creamos una nueva columna con el año de nacimiento
    autores['YearBirth'] = autores['Birthday'].apply(extraerAnio)

    # Generamos la nueva columna Country
    autores['Country'] = autores.apply(extraerPais, axis=1)
    # Seleccionamos todos los valores de Country
    countries = autores['Country'].values
    # Aplicamos la función convert a todos los valores de Country para que estandarice los nombres de los países
    standard_countries = coco.convert(names=countries, to='name_short')
    # Creamos una nueva columna con los nombres estandarizados
    autores['StandardCountry'] = standard_countries
    # Nos quedamos con el valor de StandardCountry a no se que sea 'not found', que nos quedamos con el de Country
    autores['Country'] = autores['StandardCountry'].combine(autores['Country'], lambda x, y: y if x == 'not found' else x)
    # Eliminamos la columna 'StandardCountry'
    autores.drop(columns=['StandardCountry'], inplace=True)

    # Por último eliminamo la columna NumChild ya que no es relevante
    autores = autores.drop('NumChild', axis=1)
    autores = autores.drop('Birthday', axis=1)
    autores = autores.drop('Nationality', axis=1)
    autores = autores.drop('Born', axis=1)
    autores = autores.drop('Birthplace', axis=1)

    # Reseteamos el índice
    autores = autores.reset_index(drop=True)
    autores.to_parquet('AUTORES_LIMPIOS.parquet')


    





