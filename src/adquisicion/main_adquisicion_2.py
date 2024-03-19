import pandas as pd

import adquisicion.goodreads as goodreads
import adquisicion.barnesAndNoble as barnesAndNoble
import adquisicion.googleTrends as googleTrends

import adquisicion.autoresGoodreads as autoresGoodreads
import adquisicion.autoresWikipedia as autoresWiki

def main():

    """A partir de un csv con todos los libros parcialmente limpios (sin duplicados, etc)
    obtenemos información adicional para cada libro. También obtenemos la información de los 
    autores"""

    # --- LIBROS ---

    # Obtenemos la información de GoodReads (nosotros lo hicimos con la función
    # 'getInfoGoodReadsPorPartes' que realiza el procesamiento en dos partes)
    dfLibros = getInfoGoodReads(dfLibros)

    # Obtenemos los precios de Barnes&Noble
    dfLibros = getPricesBN(dfLibros)

    # Obtenemos las medidas de tendencia de GoogleTrends
    dfLibros = googleTrends.getTrends(dfLibros)

    # Almacenamos el dataframe en formato parquet
    dfLibros.to_parquet('libros_limpios.parquet')

    # --- AUTORES ---

    # Obtenemos información de los autores a partir de la lista de libros y la almacenamos
    dfAutoresWiki = autoresWiki.generarDfAutores(dfLibros)
    dfAutoresWiki.to_csv('autores_wikipedia.csv')
    dfAutoresGoodreads = autoresGoodreads.generarDfAutoresGoodReads(dfLibros, './data')
    dfAutoresGoodreads.to_csv('autores_goodreads.csv')

def getInfoGoodReads(dfLibros):
    """A partir del dataframe con libros obtiene, para cada libro, la información
    disponible en su página de GoodReads"""
    df_info = dfLibros['Title'].apply(goodreads.getInfoLibro).apply(pd.Series)
    return pd.concat([dfLibros, df_info], axis=1)

def getInfoGoodReadsPorPartes():
    """Obtiene la información de goodreads de los libros (libros1.csv y libros2.csv) divididos 
    en 2 partes para facilitar el procesamiento"""

    for i in range(2):
        print(f"COMENZANDO PROCESAMIENTO PARTE {i + 1}")
        
        LIBROS = pd.read_csv(f"libros{i + 1}.csv")
        df_info = LIBROS['Title'].apply(goodreads.getInfoLibro).apply(pd.Series)

        LIBROS = pd.concat([LIBROS, df_info], axis=1)

        LIBROS.to_csv(f"libros_procesados_{i + 1}.csv")
        
        print(f"FINALIZANDO PROCESAMIENTO PARTE {i + 1}")

def getPricesBN(dfLibros):
    df_precios = pd.DataFrame(dfLibros['Title'].apply(barnesAndNoble.getPrice).tolist())
    dfLibros= pd.concat([dfLibros, df_precios], axis=1)
    return dfLibros

if __name__ == "__main__":
    main()
