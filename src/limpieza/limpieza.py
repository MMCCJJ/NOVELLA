import pandas as pd
from sklearn.neighbors import NearestNeighbors

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
