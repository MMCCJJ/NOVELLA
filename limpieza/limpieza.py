import pandas as pd
from sklearn.neighbors import NearestNeighbors
import re
import Levenshtein

# Columnas innecesarias que se eliminarán
COLUMNAS_INNECESARIAS = ["Main Category", "url", "Subcategory", "Publisher"]

# Formatos de libro válidos (para imputar los precios)
FORMATOS_VALIDOS = ["hardcover", "paperback", "ebook"]

# Impurezas que hemos encontrado entre los distintos autores
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

def corregirTitulos(df):
    """Corrige los títulos (capitalizar y quitar espacios en blanco en los extremos)"""
    df["Title"] = df["Title"].apply(str.capitalize).apply(str.strip)
    return df

def corregirAutores(df):
    """Corrige los nombres de los autores, eliminando espacios en blanco sobrantes y otras impurezas encontradas"""

    df["Author"] = df["Author"].apply(str.strip)

    def quitarImpurezas(x):
        for i in IMPUREZAS_AUTORES: 
            x = x.split(i, 1)[0]
        return x
        
    df["Author"] = df["Author"].apply(quitarImpurezas)
    
    return df

def extraer_primer_autor(columna_autores):
    """Extrae el nombre del primer autor (para los libros que tienen más de uno)"""

    # Divide la cadena en los casos en los que hay "with" o "and"
    split_authors = re.split(r'\s+with\s+|\s+and\s+', columna_autores)

    # Devuelve el primer autor
    return split_authors[0]

def eliminarColumnasInnecesarias(df):
    """Elimina aquellas columnas que no son relevantes"""

    df = df.drop(COLUMNAS_INNECESARIAS, axis=1)
    
    # Eliminamos columnas que contienen "unnamed"
    unnamed_columns = [col for col in df.columns if 'unnamed' in col.lower()]
    df = df.drop(unnamed_columns, axis=1)
    
    return df


def limpiarNumPaginas(df):
    """Devuelve un df cuyas filas tienen un número de páginas correcto"""

    total_libros = df.shape[0]

    # Contador para libros eliminados
    libros_eliminados = total_libros - df[df['NumPages'].apply(lambda x: re.match(r'^\d+(\.\d+)?$', str(x)) is not None)].shape[0]

    # Verificamos si el contenido de la columna NumPages es numérico
    df = df[df['NumPages'].apply(lambda x: re.match(r'^\d+(\.\d+)?$', str(x)) is not None)]

    porcentaje_eliminado = (libros_eliminados / total_libros) * 100 if total_libros != 0 else 0

    print(f"Número de libros eliminados por números de páginas incorrectos: {libros_eliminados} "
          f"({porcentaje_eliminado:.2f}% del total)")

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
    total_libros = df.shape[0]
    
    # Contador para libros eliminados por valores nulos
    libros_eliminados_nulos = total_libros - df.dropna(subset=columnasNulos).shape[0]

    df.dropna(subset=columnasNulos, inplace=True)
    
    # Contador para libros eliminados por RedPerc == -1.0
    libros_eliminados_portada = df[df['RedPerc'] == -1.0].shape[0]

    # Eliminar filas donde RedPerc es -1.0
    df = df[df['RedPerc'] != -1.0]

    porcentaje_eliminado_nulos = (libros_eliminados_nulos / total_libros) * 100 if total_libros != 0 else 0
    porcentaje_eliminado_portada = (libros_eliminados_portada / total_libros) * 100 if total_libros != 0 else 0
    
    print(f"Número de libros eliminados por valores nulos: {libros_eliminados_nulos} "
          f"({porcentaje_eliminado_nulos:.2f}% del total)")
    print(f"Número de libros eliminados donde hay un error con la portada: {libros_eliminados_portada} "
          f"({porcentaje_eliminado_portada:.2f}% del total)")

    return df


def corregirType(df):
    """Filtra y coge solo aquellas filas con un formato admitido"""
    
    FORMATOS_VALIDOS = ["ebook", "paperback", "hardcover"]
    total_libros = df.shape[0]

    # Reemplazar "kindle edition" por "ebook"
    df["Type"] = df["Type"].replace("kindle edition", "ebook")
    
    # Contador para libros eliminados por tipo no admitido
    libros_eliminados_tipo_invalido = total_libros - df[df["Type"].isin(FORMATOS_VALIDOS)].shape[0]

    # Eliminar filas que no contienen tipos admitidos
    df = df[df["Type"].isin(FORMATOS_VALIDOS)]
    
    porcentaje_eliminado_tipo_invalido = (libros_eliminados_tipo_invalido / total_libros) * 100 if total_libros != 0 else 0

    print(f"Número de libros eliminados por tipo no admitido: {libros_eliminados_tipo_invalido} "
          f"({porcentaje_eliminado_tipo_invalido:.2f}% del total)")
    
    return df

def corregirPriceFormat(df):
    """Comprueba si PriceFormat coincide con Type o si es un formato admitido,
    de lo contrario, la sustituye por el valor de Type y pone Price a nulo """
    # 1- Transformar todos los nombres de la columna PriceFormat a minúsculas
    df.loc[:, 'PriceFormat'] = df['PriceFormat'].str.lower()

    
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

def coincidenciasLevenshtein(df1, df2, umbralT=2, umbralA=2):
    """Comprueba coincidencias por parejas título-autor en función de las distancias Levenshtein,
    devuelve las coincidencias de título y autor del segundo df"""

    # Almacena los títulos y autores que coinciden del segundo df
    coincidencias = []

    df1 = df1.copy()
    df2 = df2.copy()

    # Limpiamos los títulos y los autores
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
                # Añadimos el título y autor del segundo df a la lista de coincidencias
                coincidencias.append((t2, a2))
                cont += 1

    print(f"Hay {cont} coincidencias.")

    return list(set(coincidencias))


def eliminarCoincidencias(dfBestsellers, dfLibros):
    """Elimina de un df con libros aquellas entradas que coinciden en título y autor (con una
    distancia Levenshtein puesto que son fuentes distintas) en un df de libros bestsellers"""

    # Calculamos las coincidencias
    coincidencias = coincidenciasLevenshtein(dfBestsellers, dfLibros)
    
    # Nos quedamos con aquellas entradas que no hayan tenido coincidencias
    filtro = ~dfLibros.apply(lambda x: (str(x["Title"]).upper().strip(), x["Author"].split()[0]) in coincidencias, axis=1)
    
    eliminados = dfLibros.shape[0] - sum(filtro)
    porcentajeEliminado = (eliminados / dfLibros.shape[0]) * 100 if dfLibros.shape[0] != 0 else 0
    print(f"Eliminados: {eliminados}, lo que representa un {porcentajeEliminado:.2f}% del total.")
    
    return dfLibros[filtro].reset_index(drop=True)


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
    dimIni = dfLibros.shape[0]
    dfLibros = dfLibros.drop_duplicates(subset=['Title', 'Author'], keep='first')
    dimFin = dfLibros.shape[0]
    registrosEliminados = dimIni - dimFin
    porcentajeEliminado = (registrosEliminados / dimIni) * 100 if dimIni != 0 else 0
    print(f"Se han eliminado {registrosEliminados} registros duplicados, lo que representa un {porcentajeEliminado:.2f}% del total.")
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
    
    libros_eliminados = df[~(filtro1 | filtro2)]
    num_libros_eliminados = len(libros_eliminados)
    total_libros = len(df)
    porcentaje_eliminados = (num_libros_eliminados / total_libros) * 100 if total_libros != 0 else 0
    
    print(f"Número de libros eliminados: {num_libros_eliminados} ({porcentaje_eliminados:.2f}%)")
    
    return df[filtro1 | filtro2]

def eliminarNonFiction(df):
    """Devuelve un df con los libros que no tienen la categoría 'NonFiction'"""
    
    filtroNonfic = df['GenresList'].str.lower().str.contains('nonfiction')
    
    num_total_filas = len(df)
    
    numNonFic = filtroNonfic.sum()
    numBsNonFic = df[filtroNonfic]['potencialBS'].sum()
    
    porcentaje_eliminado = (numNonFic / num_total_filas) * 100 if numNonFic != 0 else 0
    
    print(f"Número de filas eliminadas: {numNonFic} ({porcentaje_eliminado:.2f}%)")
    
    porcentaje_bs_eliminado = (numBsNonFic / num_total_filas) * 100 if numBsNonFic != 0 else 0
    
    print(f"Número de filas BS eliminadas: {numBsNonFic} ({porcentaje_eliminado:.2f}%)")
    
    
    return df[~filtroNonfic]

def corregirWeeksOnList(df):   
    """Corrige la columna WeeksOnList, añadiendo ceros donde haya Nas"""
    df["Weeks on List"].fillna(0, inplace=True)
    return df

def eliminarBestsellersPrecoces(df, mediana=20):
    """Elimina aquellas filas en las que los bestsellers sean inferiores a la mediana de días
    en que se convierten desde su publicación"""
    num_total_filas = len(df)
    
    filas_eliminadas = df[df["DaysDifference"] < mediana]
    num_filas_eliminadas = len(filas_eliminadas)
    porcentaje_eliminado = (num_filas_eliminadas / num_total_filas) * 100 if num_total_filas != 0 else 0
    
    print(f"Número de filas eliminadas: {num_filas_eliminadas} ({porcentaje_eliminado:.2f}%)")
    
    return df[df["DaysDifference"] >= mediana]


def prevBestSellersAutores(df):
    """ Devuelve el df de entrada (todos los libros) con una nueva columna que indica el número de
    bestsellers que tiene el mismo autor en la tabla con fecha previa a cada fila"""
    
    # Renombramos la columna de autores por si acaso
    df.rename(columns={'Auth': 'Author'}, inplace=True)
    
    # Tratamos los valores missing de autores
    df['Author'] = df['Author'].fillna('')
    
    # Ordenamos el df por fecha
    df = df.sort_values(by='Date')
    
    # Agrupamos por autor y contamos las instancias de bestsellers anteriores
    # (sin contar la propia fila)
    df['PrevBestSellAuthor'] = df.groupby('Author')['potencialBS'].cumsum() - df['potencialBS']
    
    return df

def gestionarFechasParaTrends(df):
    """Filtra y prepara las fechas para que puedan ser analizadas por GoogleTrends"""

    DIAS = 20
    total_filas = len(df)

    # Nos quedamos con aquellos libros que son bestsellers
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

    # Nos quedamos ahora con los no bestsellers
    df2 = df[df["potencialBS"] == 0]
    df2['DatePublished'] = pd.to_datetime(df2['DatePublished'], errors='coerce')

    out_of_bounds_dates = df2[(df2['DatePublished'].isnull())]

    # Eliminar las filas con fechas fuera de rango en df2
    df2 = df2.drop(out_of_bounds_dates.index)

    # Le sumamos la mediana para calcular la columna Date
    df2['Date'] = df2['DatePublished'] + pd.Timedelta(days=DIAS)

    # Calcular la diferencia en días entre las fechas en df2
    df2['DaysDifference'] = (df2['Date'] - df2['DatePublished']).dt.days

    df = pd.concat([df1, df2])
    df = df[df['DaysDifference'] > 0]

    num_filas_eliminadas = total_filas - len(df)
    porcentaje_eliminado = (num_filas_eliminadas / total_filas) * 100 if total_filas != 0 else 0

    print(f"Número de filas eliminadas: {num_filas_eliminadas} ({porcentaje_eliminado:.2f}%)")

    return df

def anyadirReviewsHistoricas(dfLibros, dfReviews):
    """A partir de un df de libros limpios y un df con las reviews historicas, crea dos columnas nuevas en el de libros con las reviews historicas y el numero de reviews historicas. Se encarga de que no haya duplicados y renombra las columnas del dfLibros"""
    
    # Elimina duplicados y renombra las columnas del dfReviews que tiene datos sin procesar
    dfReviews.rename(columns={'Author': 'Auth'}, inplace=True)
    dfReviews = dfReviews.drop_duplicates(subset=['Title', 'Auth'], keep='first')
    
    # Junta los dos df por la clave 'Titulo, Autor' para evitar duplicados
    df = pd.merge(dfLibros, dfReviews[['Title', 'Auth', 'Rating', 'numRatings']], on=['Title', 'Auth'], how='left')
    
    # Renombramos las columnas
    df.rename(columns={'Rating_x': 'CurrentRating', 'Rating_y': 'Rating20Days', 'numRatings': 'numRatings20Days'}, inplace=True)
    
    # Comprobamos que no se hayan añadido filas adicionales
    assert dfLibros.shape[0] == df.shape[0]
    
    # Comprobamos que se han añadido correctamente solo dos columnas
    assert dfLibros.shape[1] + 2 == df.shape[1]
    
    return df
