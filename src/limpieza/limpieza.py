import pandas as pd
from sklearn.neighbors import NearestNeighbors
import re
import Levenshtein

# Columnas innecesarias que se eliminarán
COLUMNAS_INNECESARIAS = ["Main Category", "url", "Subcategory", "Publisher"]

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

def corregirAutores(df):
    """Corrige los nombres de los autores, eliminando espacios en blanco sobrantes y otras impurezas encontradas"""

    df["Author"] = df["Author"].apply(str.strip)

    def quitarImpurezas(x):
        for i in IMPUREZAS_AUTORES: 
            x = x.split(i, 1)[0]
        return x
        
    df["Author"] = df["Author"].apply(quitarImpurezas)
    
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
    
    coincidencias = []
    
    df1 = df1.copy()
    df2 = df2.copy()
    
    df1["Title"] = df1["Title"].apply(lambda x: str(x).upper().strip())
    df2["Title"] = df2["Title"].apply(lambda x: str(x).upper().strip())
    
    df1["Author"] = df1["Author"].apply(lambda x: x.split()[0])
    df2["Author"] = df2["Author"].apply(lambda x: x.split()[0])
    
    cont = 0
    for t1, a1 in zip(df1['Title'], df1['Author']):
        for t2, a2 in zip(df2['Title'], df2['Author']):
            
            distanciaT = Levenshtein.distance(t1, t2)
            distanciaA = Levenshtein.distance(a1, a2)
            
            if distanciaT <= umbralT and distanciaA <= umbralA:
                coincidencias.append(t2)
                cont += 1
                
    print(f"Hay {cont} coincidencias.")
                
    return list(set(coincidencias))

def eliminarCoincidencias(dfBestsellers, dfLibros):
    
    titulosCoincidentes = coincidenciasLevenshtein(dfBestsellers, dfLibros)
    filtro = dfLibros["Title"].apply(lambda x: str(x).upper() not in titulosCoincidentes) 
    
    return dfLibros[filtro].reset_index(drop = True)

def crearColumnaPotencialBS(df, esPotencialBS = False):
    df["potencialBS"] = int(esPotencialBS)
    return df

def agruparTitulosBestsellers(df):
    
    agrupados = df.groupby(['Title', 'Author', 'Publisher', 'Main Category']).agg(
        {
            'Description': 'first',
            'Date': 'min', 
            'Weeks on List': 'max',
            'Subcategory': lambda x: x.tolist()
        }
    )
    
    agrupados["Subcategory"] = agrupados["Subcategory"].apply(lambda x: list(set(x)))
    
    agrupados = agrupados.sort_values(by = "Date").reset_index()
    
    return agrupados

def eliminarDuplicados(dfLibros):
    dfLibros = dfLibros.drop_duplicates(subset=['Title', 'Author'], keep='first')
    return dfLibros

def juntarLibros(dfBestsellers, dfLibros):
    
    return pd.concat(
        [
            crearColumnaPotencialBS(dfBestsellers, True),
            crearColumnaPotencialBS(dfLibros, False)
        ],
        ignore_index = True
    )

def anyadirColumna(df1, df2, columna):
    """Añade la columna especificada del DataFrame df2 al DataFrame df1 """
   
    if columna not in df2.columns:
        raise ValueError(f"La columna '{columna}' no existe en el segundo DataFrame.")

    df = pd.merge(df1, df2[['Title', 'Author' ,columna]], on=['Title', 'Author'], how = 'left')
    
    return df

def corregirWeeksOnList(df):   
    df["Weeks on List"].fillna(0, inplace=True)
    return df

def eliminarBestsellersPrecoces(df, mediana = 20):
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
    
    # Agrupamos por autor y contamos las instancias
    df_exploded['cumulative_count'] = df_exploded.groupby('Author').cumcount()
    
    # Guardamos el número máximo de bestsellers anteriores de la tabla en el df original
    df = pd.merge(df, df_exploded.groupby('Title')['cumulative_count'].max().reset_index(), on='Title', how='left')
    df = df.rename(columns={'cumulative_count': 'PrevBestSellAuthor'})

    # Los que no sean bestsellers deben tener esta nueva variable a cero
    df.loc[df['potencialBS'] == 0, 'PrevBestSellAuthor'] = 0
    
    return df
