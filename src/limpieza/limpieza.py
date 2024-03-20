import pandas as pd
from sklearn.neighbors import NearestNeighbors
import re
import Levenshtein

# Columnas innecesarias que se eliminarán
COLUMNAS_INNECESARIAS = ["Main Category", "url", "Subcategory", "Publisher"]


# Formatos de libro válidos (para imputar los precios)
FORMATOS_VALIDOS = ["hardcover", "paperback", "ebook"]

def corregirTitulos(df):
    """Corrige los títulos (capitalizar y quitar espacios en blanco en los extremos)"""
    df["Title"] = df["Title"].apply(str.capitalize).apply(str.strip)
    return df

def eliminarColumnasInnecesarias(df):
    """Elimina aquellas columnas que no son relevantes"""

    df = df.drop(COLUMNAS_INNECESARIAS, axis=1)
    
    # Eliminamos columnas que contienen "unnamed"
    unnamed_columns = [col for col in df.columns if 'unnamed' in col.lower()]
    df = df.drop(unnamed_columns, axis=1)
    
    return df


def limpiarNumPaginas(df):
    """Devuelve un df cuyas filas tienen un número de páginas correcto"""

    # Verificamos si el contenido de la columna NumPages es numérico
    df = df[df['NumPages'].apply(lambda x: str(x).isdigit())]
    
    return df

def limpiarSagas(df):
    """Crea una columna que indica si pertenece a una saga o no, elimina la columna SagaName y corrige SagaNumber"""

    # Verificamos si la columna SagaName es un string y la columna SagaNumber es un int
    df['BelongSaga'] = df['SagaName'].apply(lambda x: isinstance(x, str))

    # Convertimos SagaNumber a entero
    df['SagaNumber'] = df['SagaNumber'].apply(lambda x: int(x) if str(x).isdigit() else (int(float('.'.join(str(x).split('.')[-1:]))) if '.' in str(x) else 1))
    
    # Si no cumple la condición anterior, asignar 1 a SagaNumber y False a BelongSaga
    df.loc[~df['BelongSaga'], 'SagaNumber'] = 1
    df.loc[~df['BelongSaga'], 'BelongSaga'] = False
    
    # Eliminamos la columna SagaName
    df.drop(columns=['SagaName'], inplace=True)
    
    return df

def eliminarNulos(df):
    """Elimina columnas en las que hay valores nulos de variables importantes"""
    
    columnasNulos = ["Rating", "NumPages", "GenresList"]
    df.dropna(subset=columnasNulos, inplace=True)
    
    # Eliminar filas donde RedPerc es -1.0
    df = df[df['RedPerc'] != -1.0]
    
    return df

def corregirType(df):
    """Filtra y coge solo aquellas filas con un formato admitido"""
    
    # Reemplazar "kindle edition" por "ebook"
    df["Type"] = df["Type"].replace("kindle edition", "ebook")
    # Eliminar filas que no contienen tipos admitidos
    df = df[df["Type"].isin(FORMATOS_VALIDOS)]
    
    return df
    
def corregirPriceFormat(df):
    """Comprueba si PriceFormat coincide con Type o si es un formato admitido,
    de lo contrario, la sustituye por el valor de Type y pone Price a nulo """
    # 1- Transformar todos los nombres de la columna PriceFormat a minúsculas
    df['PriceFormat'] = df['PriceFormat'].str.lower()
    
    # 2- Contrastar esa columna con la columna Type
    for index, row in df.iterrows():
        if row['PriceFormat'] != row['Type']:
            # Si no coinciden y no es uno de los valores permitidos
            if row['PriceFormat'] not in FORMATOS_VALIDOS:
                # Reemplazar el valor de PriceFormat por el de la columna Type
                df.at[index, 'PriceFormat'] = row['Type']
                # El campo Price se pone a nulo
                df.at[index, 'Price'] = None
                
    return df


def imputarPrecios(df, vecinos = 5):
    """Imputa los precios en la columna Price de los valores nulos"""
    
    # Convertimos PriceFormat en variables dummy
    df = pd.get_dummies(df, columns=['PriceFormat'])
    
    # Filtramos nulos en la columna Price
    df_nulos = df[df['Price'].isnull()]
    
    # Filtramos no nulos en la columna 'Price'
    df_no_nulos = df.dropna(subset=['Price'])
    
    # Seleccionamos las características relevantes para el algoritmo KNN
    X = df_no_nulos[['NumPages', 'Rating', 'PriceFormat_hardcover', 'PriceFormat_paperback', 'PriceFormat_ebook']]
    y = df_no_nulos['Price']
    
    # Inicializamos el modelo KNN
    knn = NearestNeighbors(n_neighbors=vecinos)
    knn.fit(X, y)
    
    # Iteramos sobre los nulos para imputar
    for index, row in df_nulos.iterrows():
        
        # Filtramos libros similares
        libroSimilarIndices = knn.kneighbors(
            
            [[row['NumPages'], 
              row['Rating'], 
              row['PriceFormat_hardcover'], 
              row['PriceFormat_paperback'], 
              row['PriceFormat_ebook']]]
        )[1][0]
        
        librosSimilares = df_no_nulos.iloc[libroSimilarIndices]
        
        # Calculamos la media de los precios de los libros similares
        precioImputado = round(librosSimilares['Price'].mean(), 2)
       
        # Imputamos el precio
        df.at[index, 'Price'] = precioImputado
    
    # Eliminamos el one-hot encoding
    df['PriceFormat'] = df[['PriceFormat_hardcover', 'PriceFormat_paperback', 'PriceFormat_ebook']].idxmax(axis=1).str.replace('PriceFormat_', '')
    df = df.drop(['PriceFormat_hardcover', 'PriceFormat_paperback', 'PriceFormat_ebook'], axis=1)
    
    return df

def coincidenciasLevenshtein(df1, df2, umbralT = 2, umbralA = 2):
    """Comprueba coincidencias por parejas título-autor en función de las distancias Levenshtein,
    devuelve los títulos coincidentes del segundo df """

    # Almacena los títulos que coinciden del segundo df
    coincidencias = []
    

    df1 = df1.copy()
    df2 = df2.copy()
    
    # Limpiamos los títulos y los autores
    df1["Title"] = df1["Title"].apply(lambda x: str(x).upper().strip())
    df2["Title"] = df2["Title"].apply(lambda x: str(x).upper().strip())
    
    df1["Author"] = df1["Author"].apply(lambda x: x.split()[0])
    df2["Author"] = df2["Author"].apply(lambda x: x.split()[0])
    
    cont = 0

    # Recorremos todas las combinaciones entre parejas
    for t1, a1 in zip(df1['Title'], df1['Author']):
        for t2, a2 in zip(df2['Title'], df2['Author']):
            
            # Calculamos distancias Levenshtein
            distanciaT = Levenshtein.distance(t1, t2)
            distanciaA = Levenshtein.distance(a1, a2)
            
            # Si las distancias en ambos (título-autor) son menores que el umbral -> HAY COINCIDENCIA
            if distanciaT <= umbralT and distanciaA <= umbralA:
                # Añadimos el título del segundo df a la lista de coincidencias
                coincidencias.append(t2)
                cont += 1
                
    print(f"Hay {cont} coincidencias.")
                
    return list(set(coincidencias))

def eliminarCoincidencias(dfBestsellers, dfLibros):
    """Elimina de un df con libros aquellas entradas que coinciden en título y autor (con una
    distancia Levenshtein puesto que son fuentes distintas) en un df de libros bestsellers"""

    # Calculamos las coincidencias
    titulosCoincidentes = coincidenciasLevenshtein(dfBestsellers, dfLibros)
    # Nos quedamos con aquellas entradas que no hayan tenido coincidencias
    filtro = dfLibros["Title"].apply(lambda x: str(x).upper() not in titulosCoincidentes) 
    
    return dfLibros[filtro].reset_index(drop = True)

def crearColumnaPotencialBS(df, esPotencialBS = False):
    """Crea una columna indicando si el libro es un bestseller potencial (1) o no (0)"""
    df["potencialBS"] = int(esPotencialBS)
    return df

def agruparTitulosBestsellers(df):
    """Agrupa los libros bestsellers de un df, quedándose con la primera fecha de aparición y con
    el máximo de semanas que lleva en la lista"""

    # Agrupamos los datos
    agrupados = df.groupby(['Title', 'Author', 'Main Category']).agg(
        {
            'Description': 'first',
            'Date': 'min', 
            'Weeks on List': 'max',
            'Subcategory': lambda x: x.tolist()
        }
    )
    
    # Convertimos las subcategorías en una lista con valores no duplicados
    agrupados["Subcategory"] = agrupados["Subcategory"].apply(lambda x: list(set(x)))
    
    # Ordenamos los libros por fecha
    agrupados = agrupados.sort_values(by = "Date").reset_index()
    
    return agrupados

def eliminarDuplicados(dfLibros):
    """Elimina entradas duplicadas con respecto a la clave Título-Autor"""
    dfLibros = dfLibros.drop_duplicates(subset=['Title', 'Author'], keep='first')
    return dfLibros

def juntarLibros(dfBestsellers, dfLibros):
    """Combina libros bestsellers y no bestsellers, para distinguirlos crea la columna
    PotencialBS, que indica si es BS o no"""
    return pd.concat(
        [
            crearColumnaPotencialBS(dfBestsellers, True),
            crearColumnaPotencialBS(dfLibros, False)
        ],
        ignore_index = True
    )

def anyadirColumna(df1, df2, columna):
    """Añade la columna especificada del DataFrame df2 al DataFrame df1"""
   
    if columna not in df2.columns:
        raise ValueError(f"La columna '{columna}' no existe en el segundo DataFrame.")

    df = pd.merge(df1, df2[['Title', 'Author' ,columna]], on=['Title', 'Author'], how = 'left')
    
    return df

def contieneFiccion(cadena):
    """Verifica que una cadena de texto contiene Fiction"""
    lista = str(cadena).strip("[]").replace("'", "").split(", ")
    return 'Fiction' in lista

def soloFiccion(df):
    """Devuelve un df solo con los libros de categoría ficción"""
    filtro1 = df["Main Category"] == "FICTION"
    filtro2 = df["GenresList"].apply(contieneFiccion)
    
    return df[filtro1 | filtro2]

def corregirWeeksOnList(df):   
    """Corrige la columna WeeksOnList, añadiendo ceros donde haya Nas"""
    df["Weeks on List"].fillna(0, inplace=True)
    return df

def eliminarBestsellersPrecoces(df, mediana = 20):
    """Elimina aquellas filas en las que los bestsellers sean inferiores a la mediana de días
    en que se convierten desde su publicación"""
    return df[df["DaysDifference"] >= mediana]

def prevBestSellersAutores(df):
    """ Devuelve el df de entrada (todos los libros) con una nueva columna que indica el número de
    bestsellers que tiene el mismo autor en la tabla con fecha previa a cada fila"""

    # Tratamos los valores missing de autores
    df['Author'] = df['Author'].fillna('')

    # Sacamos los autores individuales en formato lista
    df['Author'] = df['Author'].apply(lambda x: re.split(r'\band\b|\bwith\b|\s*,\s*', x))

    # Creamos un df con un autor por fila y ordenamos por fecha
    df_exploded = df.explode('Author')
    df_exploded = df_exploded.sort_values(by='Date')
    
    # Agrupamos por autor y contamos las instancias de bestsellers anteriores
    # (sin contar la propia fila)
    df_exploded['PrevBestSellAuthor'] = df_exploded.groupby('Authors')['potencialBS'].cumsum() - df_exploded['potencialBS']
    
    # Guardamos el número máximo de bestsellers anteriores de la tabla en el df original
    max_prev_bestsellers = df_exploded.groupby('Title')['PrevBestSellAuthor'].max().reset_index()
    df = pd.merge(df, max_prev_bestsellers, on='Title', how='left')
    
    # Reemplazamos los valores nulos con 0
    df['PrevBestSellAuthor'] = df['PrevBestSellAuthor'].fillna(0).astype(int)
    
    return df

def gestionarFechasParaTrends(df):
    """Filtra y prepara las fechas para que puedan ser analizadas por GoogleTrends"""

    DIAS = 20
    
    # Nos quedamos con aquellos libros que son bestsellers
    df1 = df[df["potencialBS"] == 1]

    # Convertir las columnas a tipo de dato de fecha
    df1['Date'] = pd.to_datetime(df1['Date'], errors='coerce')
    df1['DatePublished'] = pd.to_datetime(df1['DatePublished'], errors='coerce')

    # Encontrar las fechas que están fuera del rango permitido
    out_of_bounds_dates = df1[(df1['Date'].isnull()) | (df1['DatePublished'].isnull())]

    df1 = df1.drop(out_of_bounds_dates.index)

    df1['Date'] = pd.to_datetime(df1['Date'])
    df1['DatePublished'] = pd.to_datetime(df1['DatePublished'])
    df1['DaysDifference'] = (df1['Date'] - df1['DatePublished']).dt.days
    
    # Nos quedamos ahora con los no bestsellers
    df2 = df[df["potencialBS"] == 0]
    df2['DatePublished'] = pd.to_datetime(df2['DatePublished'], errors='coerce')

    out_of_bounds_dates = df2[(df2['DatePublished'].isnull())]

    # Eliminar las filas con fechas fuera de rango en df2
    df2 = df2.drop(out_of_bounds_dates.index)

    # Le sumamos la mediana para calcular la columna Date
    df2['Date'] = df2['DatePublished'] + pd.Timedelta(days= DIAS)

    # Calcular la diferencia en días entre las fechas en df2
    df2['DaysDifference'] = (df2['Date'] - df2['DatePublished']).dt.days
    
    df = pd.concat([df1, df2])
    df = df[df['DaysDifference'] > 0]

    return df
