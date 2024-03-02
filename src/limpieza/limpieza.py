import pandas as pd

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